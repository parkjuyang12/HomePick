import json
import hashlib
import re
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

# 거래 스트림 처리 파이프라인
# - Kafka에서 자산 거래 이벤트 소비(JSON)
# - property_id 생성 후 동일 ID별 stateful 집계
# - 최신 거래/거래 횟수는 current, 모든 거래는 history로 분기
# - 현재는 콘솔로만 출력(ES 연동 전 단계)

# =========================
# 설정: Kafka 입력 소스 정의 (중앙화된 설정 사용)
# =========================
from config import KAFKA_BROKERS, KAFKA_TOPICS, KAFKA_GROUP_ID

# =========================
# property_id 생성: 자산 타입별 주요 식별자 조합
# =========================
def make_property_id(event: dict) -> str:
    """
    건물/단지 기준 식별자
    """
    asset = event.get("asset_type", "UNKNOWN")
    lawd = event.get("lawd_cd", "UNKNOWN")
    p = event.get("payload", {})

    def _normalize(s: str) -> str:
        if s is None:
            return ""
        raw = str(s).strip()
        # 와일드카드(*)는 식별자 혼선을 줄이기 위해 제거
        raw = re.sub(r'\*+', '', raw)
        # 허용 문자만 남기기(숫자, 영문, 한글, 하이픈, 공백, '~' 근사표시)
        s = re.sub(r'[^0-9a-zA-Z가-힣\-\s~]', "", raw)
        s = re.sub(r'\s+', " ", s)
        return s

    if asset == "APARTMENT":
        human = _normalize(p.get("aptSeq") or p.get("aptNm") or "")
    elif asset == "HOUSE":
        umd = _normalize(p.get("umdNm"))
        jibun = _normalize(p.get("jibun"))
        mhouse = _normalize(p.get("mhouseNm") or "")
        human = "|".join([x for x in [umd, jibun, mhouse] if x])
    elif asset == "OFFICETEL":
        human = _normalize(p.get("offiSeq") or p.get("offiNm") or p.get("roadNm") or "")
    elif asset == "COMMERCIAL":
        human = _normalize(p.get("buildSeq") or p.get("roadNm") or "")
    else:
        human = _normalize(p.get("roadNm") or "")

    # 안전: 빈 항목으로 인한 불필요한 구분자 제거
    human = human.strip(' |')

    base = f"{asset}|{lawd}|{human}"
    short_hash = hashlib.sha256(base.encode("utf-8")).hexdigest()[:8]
    canonical_id = f"{base}|{short_hash}"
    return canonical_id

# =========================
# Keyed Process Function: 같은 property_id끼리 집계/분기
# =========================
class PropertyAggregator(KeyedProcessFunction):

    def open(self, runtime_context):
        # 최근 거래일자, 최근 가격, 거래 횟수 상태 유지
        self.latest_date = runtime_context.get_state(ValueStateDescriptor("latest_date", Types.STRING()))
        self.latest_price = runtime_context.get_state(ValueStateDescriptor("latest_price", Types.INT()))
        self.trade_count = runtime_context.get_state(ValueStateDescriptor("trade_count", Types.INT()))

    def process_element(self, event, ctx):
        p = event["payload"]

        # 거래 날짜/금액 정규화
        deal_date = int(
            f"{p.get('dealYear')}{int(p.get('dealMonth')):02d}{int(p.get('dealDay')):02d}"
        )

        # 안전한 숫자 파싱: 문자열(쉼표 포함) 또는 정수 모두 처리
        def _to_int(val):
            if val is None:
                return 0
            if isinstance(val, int):
                return val
            try:
                return int(str(val).replace(",", ""))
            except Exception:
                return 0

        price = _to_int(p.get("dealAmount") or p.get("deposit") or 0)

        # 거래 수 증가 및 상태 업데이트
        count = self.trade_count.value() or 0
        count += 1
        self.trade_count.update(count)

        # 최신 거래 판단(더 최근이면 최신 거래 상태 갱신)
        prev_date = self.latest_date.value()
        if prev_date is None or deal_date > int(prev_date):
            self.latest_date.update(str(deal_date))
            self.latest_price.update(price)

        property_doc = {
            "property_id": event["property_id"],
            "asset_type": event["asset_type"],
            "lawd_cd": event["lawd_cd"],
            "latest_trade": {
                "price": price,
                "deal_date": deal_date,
            },
            "trade_count": count,
            "updated_at": datetime.utcnow().isoformat(),
        }

        history_doc = {
            "property_id": event["property_id"],
            "trade_fingerprint": event["fingerprint"],
            "price": price,
            "deal_date": deal_date,
            "floor": p.get("floor"),
            "area": p.get("excluUseAr"),
            "occurred_at": event["occurred_at"],
        }

        # 두 스트림으로 분기(current는 업서트, history는 append)
        yield ("current", property_doc)
        yield ("history", history_doc)

# =========================
# Main
# =========================
def run():
    # 단일 파이프라인: Kafka → JSON 파싱 → property_id 생성 → key별 집계 → current/history 분기 출력
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.enable_checkpointing(60000)
    # 체크포인트를 파일 시스템에 저장하여 재시작 후 복원 가능하도록 설정
    env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
    env.get_checkpoint_config().enable_externalized_checkpoints(
        ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
    )
    # 자동 재시작 설정 (장애 발생 시 Flink 자체 복구로 다시 실행되어 체크포인트 오프셋으로 이어서 처리)
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 1000))

    # starting offsets: prefer committed offsets, fallback to latest when Java-side enums are unavailable
    try:
        starting_offsets = KafkaOffsetsInitializer.committed_offsets()
    except Exception as e:
        print(f"[WARN] KafkaOffsetsInitializer.committed_offsets() unavailable: {e}; falling back to latest")
        starting_offsets = KafkaOffsetsInitializer.latest()

    source = (
        KafkaSource.builder()
        .set_bootstrap_servers(KAFKA_BROKERS)
        # set_topics expects varargs; unpack 리스트로 전달
        .set_topics(*KAFKA_TOPICS)
        .set_group_id(KAFKA_GROUP_ID)
        .set_starting_offsets(starting_offsets)
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    stream = env.from_source(
        source,
        WatermarkStrategy.no_watermarks(),
        "KafkaSource"
    )

    parsed = stream.map(lambda x: json.loads(x))

    with_property = parsed.map(
        lambda e: {**e, "property_id": make_property_id(e)}
    )

    aggregated = (
        with_property
        .key_by(lambda e: e["property_id"])
        .process(PropertyAggregator())
    )

    # ========================
    # Elastic Search Sink 연결 (HTTP 기반 임시 구현; map으로 사이드이펙트 전송)
    # ========================
    aggregated.map(create_current_sink())
    aggregated.map(create_history_sink())

    env.execute("RealEstate Property Aggregation Job")

if __name__ == "__main__":
    run()
