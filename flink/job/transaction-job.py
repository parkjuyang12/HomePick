import json
import hashlib
import re
import os
from datetime import datetime

from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.datastream.checkpoint_config import ExternalizedCheckpointCleanup
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.common.restart_strategy import RestartStrategies
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy

from sinks import create_current_sink, create_history_sink

# =========================
# 설정: Kafka 입력 소스 정의 (중앙화된 설정 사용)
# =========================
from config import KAFKA_BROKERS, KAFKA_TOPICS, KAFKA_GROUP_ID

# =========================================================
# Utils (string/number cleanup)
# =========================================================
def normalize_str(v) -> str:
    return "" if v is None else str(v).strip()

def clean_jibun(v) -> str:
    if v is None:
        return ""
    v = re.sub(r"\*+", "", str(v))
    return re.sub(r"\s+", " ", v).strip()

def to_int(v):
    if v is None:
        return 0
    try:
        return int(str(v).replace(',', ''))
    except Exception:
        return 0

# =========================================================
# Price parsing (TRADE vs RENT)
# =========================================================
def parse_price(payload: dict, transaction_type: str):
    """
    - TRADE: price(dealAmount)
    - RENT : deposit + monthly_rent
    Returns: (price, deposit, monthly_rent)
    """
    price = deposit = monthly_rent = None

    if transaction_type == "TRADE":
        price = to_int(payload.get("dealAmount"))

    elif transaction_type == "RENT":
        deposit = to_int(payload.get("deposit"))
        monthly_rent = to_int(payload.get("monthlyRent"))

    return price, deposit, monthly_rent

# =========================================================
# Address builders
# =========================================================
def build_apartment_address(payload: dict) -> dict:
    raw = normalize_str(payload.get("jibun"))
    jibun = clean_jibun(raw) if raw and "*" not in raw else ""
    return {
        "umd": normalize_str(payload.get("umdNm")),
        "road": normalize_str(payload.get("roadNm")),
        "jibun": jibun,

        "display": " ".join([
            normalize_str(payload.get("umdNm")),
            normalize_str(payload.get("aptNm")),
            normalize_str(payload.get("aptDong"))
        ]).strip(),
    }

def build_house_address(payload: dict) -> dict:
    raw = normalize_str(payload.get("jibun"))
    jibun = clean_jibun(raw) if raw and "*" not in raw else ""
    
    return {
        "umd": normalize_str(payload.get("umdNm")),
        "jibun": jibun,
        "house_type": normalize_str(payload.get("houseType")),

        "display": " ".join([
            normalize_str(payload.get("umdNm")),
            jibun
        ]).strip(),
    }

def build_officetel_address(payload: dict) -> dict:
    name = normalize_str(payload.get("offiNm"))
    raw = normalize_str(payload.get("jibun"))
    jibun = clean_jibun(raw) if raw and "*" not in raw else ""

    return {
        "sgg": normalize_str(payload.get("sggNm")),
        "umd": normalize_str(payload.get("umdNm")),
        "jibun": jibun,
        "name": name,

        "display": " ".join([
            normalize_str(payload.get("umdNm")),
            name
        ]).strip(),
    }

def build_commercial_address(payload: dict) -> dict:
    name = normalize_str(payload.get("offiNm"))
    raw = normalize_str(payload.get("jibun"))
    jibun = clean_jibun(raw) if raw and "*" not in raw else ""

    return {
        "sgg": normalize_str(payload.get("sggNm")),
        "umd": normalize_str(payload.get("umdNm")),
        "jibun": jibun,
        "name": name,

        "display": " ".join([
            normalize_str(payload.get("umdNm")),
            name
        ]).strip(),
    }

# =========================================================
# Address builders
#   - current: rich(기존 로직 유지)
#   - history: common(minimal)
# =========================================================
def build_current_address(event: dict, payload: dict) -> dict:
    asset = event.get("asset_type")

    if asset == "APARTMENT":
        return build_apartment_address(payload)

    if asset == "HOUSE":
        return build_house_address(payload)

    if asset == "OFFICETEL":
        return build_officetel_address(payload)

    if asset == "COMMERCIAL":
        return build_commercial_address(payload)

    return {}


# =========================================================
# property_id 생성: 자산 타입별 주요 식별자 조합 (그대로 유지)
# =========================================================
def make_property_id(event: dict) -> str:
    """
    건물/단지 기준 식별자 (address builder 설계에 맞춘 버전)
    - asset_type별로 키를 명확히 분리
    - HOUSE의 jibun 마스킹(*** 포함) 방어
    - build_*_address에서 쓰는 핵심 값들을 우선 활용
    """
    asset = event.get("asset_type", "UNKNOWN")
    lawd = event.get("lawd_cd", "UNKNOWN")
    p = event.get("payload", {})

    # 기존 _normalize는 유지(식별자용 정규화)
    def _normalize(s: str) -> str:
        if s is None:
            return ""
        raw = str(s).strip()
        raw = re.sub(r"\*+", "", raw)  # '*' 제거
        s2 = re.sub(r"[^0-9a-zA-Z가-힣\-\s~]", "", raw)
        s2 = re.sub(r"\s+", " ", s2)
        return s2.strip()

    # 공통 후보 값
    umd = _normalize(p.get("umdNm"))
    road = _normalize(p.get("roadNm"))
    offi_name = _normalize(p.get("offiNm"))
    apt_seq = _normalize(p.get("aptSeq"))
    apt_name = _normalize(p.get("aptNm"))

    # jibun: HOUSE에서 마스킹 들어올 수 있으니 '*' 포함이면 배제
    raw_jibun = normalize_str(p.get("jibun"))
    jibun = ""
    if raw_jibun and ("*" not in raw_jibun):
        jibun = _normalize(raw_jibun)

    if asset == "APARTMENT":
        # 아파트는 aptSeq가 가장 안정적 (없으면 aptNm)
        human = apt_seq or apt_name

    elif asset == "HOUSE":
        # 주택은 (umd + jibun) 중심. jibun이 마스킹이면 umd만 사용
        # (mhouseNm은 데이터가 불안정해서 기본 키에서 제외하고 싶으면 빼도 됨)
        mhouse = _normalize(p.get("mhouseNm") or "")
        parts = [x for x in [umd, jibun, mhouse] if x]
        human = "|".join(parts) if parts else umd

    elif asset == "OFFICETEL":
        # 오피스텔은 이름/시퀀스가 있으면 우선, 없으면 (umd + jibun)으로 fallback
        offi_seq = _normalize(p.get("offiSeq"))
        human = offi_seq or offi_name
        if not human:
            parts = [x for x in [umd, jibun] if x]
            human = "|".join(parts) if parts else road

    elif asset == "COMMERCIAL":
        # 상가는 buildSeq가 없고 offiNm로 오는 케이스가 많아서 offiNm 우선
        build_seq = _normalize(p.get("buildSeq"))
        human = build_seq or offi_name
        if not human:
            parts = [x for x in [umd, jibun, road] if x]
            human = "|".join(parts) if parts else umd

    else:
        # 기타는 최대한 충돌 적게: (umd + jibun + road)
        parts = [x for x in [umd, jibun, road] if x]
        human = "|".join(parts) if parts else "UNKNOWN"

    human = human.strip(" |")

    base = f"{asset}|{lawd}|{human}"
    short_hash = hashlib.sha256(base.encode("utf-8")).hexdigest()[:8]
    return f"{base}|{short_hash}"

# =========================================================
# Document builders
# =========================================================
def build_current_detail(asset: str, payload: dict) -> dict:
    """
    건물 유형별 '현재 상태' 상세 정보
    - 지도/리스트/상세 진입에 쓰이는 정보
    """
    if asset == "APARTMENT":
        return {
            "build_year": payload.get("buildYear"),
            "apt_dong": normalize_str(payload.get("aptDong")),
        }

    if asset == "HOUSE":
        return {
            "house_type": normalize_str(payload.get("houseType")),
            "build_year": payload.get("buildYear"),
        }

    if asset == "OFFICETEL":
        return {
            "build_year": payload.get("buildYear"),
        }

    if asset == "COMMERCIAL":
        return {
            "build_year": payload.get("buildYear"),
        }

    return {}

def build_history_detail(asset: str, payload: dict) -> dict:
    """
    history는 '거래 시점 정보'만 보존
    """
    if asset == "APARTMENT":
        return {
            "buyer_type": payload.get("buyerGbn"),
            "sler_type": payload.get("slerGbn"),
            "deal_method": payload.get("dealingGbn"),

            "area": payload.get("excluUseAr"),
            "floor": payload.get("floor"),
        }
    if asset == "HOUSE":
        return {
            "buyer_type": payload.get("buyerGbn"),
            "sler_type": payload.get("slerGbn"),
            "deal_method": payload.get("dealingGbn"),

            "plottage": payload.get("plottageAr"),
            "total_floor_area": payload.get("totalFloorAr"),
        }
    if asset == "OFFICETEL":
        return {
            "buyer_type": payload.get("buyerGbn"),
            "sler_type": payload.get("slerGbn"),
            "deal_method": payload.get("dealingGbn"),

            "area": payload.get("excluUseAr"),
            "floor": payload.get("floor"),
        }
    if asset == "COMMERCIAL":
        return {
            "buyer_type": payload.get("buyerGbn"),
            "sler_type": payload.get("slerGbn"),
            "deal_method": payload.get("dealingGbn"),

            "area": payload.get("excluUseAr"),
            "floor": payload.get("floor"),
        }
    
    return {}

def build_current_doc(event, payload, deal_date, price, deposit, monthly_rent, count, latest_price, latest_tx_type):
    return {
        "asset_type": event["asset_type"],
        "property_id": event["property_id"],
        "lawd_cd": event["lawd_cd"],

        "latest_trade": {
            "transaction_type": latest_tx_type,
            "price": latest_price,
            "deal_date": deal_date,
        },

        "trade_count": count,
        "address": build_current_address(event, payload),
        "detail": build_current_detail(event["asset_type"], payload),

        "updated_at": datetime.utcnow().isoformat(),
    }

def build_history_doc(event, payload, deal_date, price, deposit, monthly_rent):
    return {
        "asset_type": event["asset_type"],
        "property_id": event["property_id"],
        "transaction_type": event["transaction_type"],

        "trade_fingerprint": event["fingerprint"],
        "deal_date": deal_date,

        "price": price,
        "deposit": deposit,
        "monthly_rent": monthly_rent,

        "detail": build_history_detail(event["asset_type"], payload),

        "occurred_at": event["occurred_at"],
    }

# =========================================================
# Keyed Process Function: 같은 property_id끼리 집계/분기
# =========================================================
class PropertyAggregator(KeyedProcessFunction):
    def open(self, runtime_context):
        self.latest_date = runtime_context.get_state(
            ValueStateDescriptor("latest_date", Types.STRING())
        )
        self.latest_price = runtime_context.get_state(
            ValueStateDescriptor("latest_price", Types.INT())
        )
        self.latest_tx_type = runtime_context.get_state(   # ⭐ 추가
        ValueStateDescriptor("latest_tx_type", Types.STRING())
        )
        self.trade_count = runtime_context.get_state(
            ValueStateDescriptor("trade_count", Types.INT())
        )

    def process_element(self, event, ctx):
        payload = event["payload"]
        tx_type = event.get("transaction_type")

        deal_date = int(
            f"{payload.get('dealYear')}{int(payload.get('dealMonth')):02d}{int(payload.get('dealDay')):02d}"
        )

        price, deposit, monthly_rent = parse_price(payload, tx_type)

        count = (self.trade_count.value() or 0) + 1
        self.trade_count.update(count)

        prev_date = self.latest_date.value()
        if prev_date is None or deal_date > int(prev_date):
            self.latest_date.update(str(deal_date))
            self.latest_price.update(price or deposit or monthly_rent)
            self.latest_tx_type.update(tx_type)   

        latest_deal_date = int(self.latest_date.value())
        latest_price = self.latest_price.value()
        latest_tx_type = self.latest_tx_type.value() or tx_type

        current_doc = build_current_doc(
            event, payload,
            latest_deal_date,
            price, deposit, monthly_rent,
            count, latest_price,
            latest_tx_type
        )

        history_doc = build_history_doc(
            event, payload,
            deal_date, price, deposit, monthly_rent
        )

        yield ("current", current_doc)
        yield ("history", history_doc)



# =========================
# Main (ES 연결 / Flink 설정 / Kafka 설정 건드리지 않음)
# =========================
def run():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.enable_checkpointing(60000)

    env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
    env.get_checkpoint_config().enable_externalized_checkpoints(
        ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
    )
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 1000))

    # starting offsets strategy (env var KAFKA_STARTING_OFFSETS: committed|earliest|latest)
    start_mode = os.getenv("KAFKA_STARTING_OFFSETS", "committed").lower()

    starting_offsets = None
    if start_mode == "committed":
        try:
            starting_offsets = KafkaOffsetsInitializer.committed_offsets()
        except Exception as e:
            print(f"[WARN] committed_offsets unavailable: {e}; falling back to earliest")
            starting_offsets = KafkaOffsetsInitializer.earliest()
    elif start_mode == "earliest":
        starting_offsets = KafkaOffsetsInitializer.earliest()
    else:
        starting_offsets = KafkaOffsetsInitializer.latest()

    print(f"[INFO] Kafka starting offsets strategy: {start_mode}")

    # wait for kafka broker to be reachable (avoid Flink startup failure when broker absent)
    def _wait_for_kafka(brokers, timeout_sec=30):
        import socket, time

        first = str(brokers).split(",")[0]
        host, port = first.split(":")
        port = int(port)

        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            try:
                with socket.create_connection((host, port), timeout=2):
                    print(f"[INFO] Kafka broker reachable: {host}:{port}")
                    return True
            except Exception:
                time.sleep(1)

        raise RuntimeError(f"Kafka broker not reachable at {host}:{port}")

    _wait_for_kafka(KAFKA_BROKERS, timeout_sec=int(os.getenv("KAFKA_WAIT_TIMEOUT", "30")))

    source = (
        KafkaSource.builder()
        .set_bootstrap_servers(KAFKA_BROKERS)
        .set_topics(*KAFKA_TOPICS)
        .set_group_id(KAFKA_GROUP_ID)
        .set_starting_offsets(starting_offsets)
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    stream = env.from_source(source, WatermarkStrategy.no_watermarks(), "KafkaSource")
    parsed = stream.map(lambda x: json.loads(x))

    with_property = parsed.map(lambda e: {**e, "property_id": make_property_id(e)})

    aggregated = (
        with_property
        .key_by(lambda e: e["property_id"])
        .process(PropertyAggregator())
    )

    # ========================
    # Elastic Search Sink 연결 (절대 변경하지 않음)
    # ========================
    aggregated.map(create_current_sink())
    aggregated.map(create_history_sink())

    env.execute("RealEstate Property Aggregation Job")


if __name__ == "__main__":
    run()
