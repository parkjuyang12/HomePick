# main.py (상단)
import json
import hashlib
from datetime import datetime


# 유일한 거래 ID 생성(식별자)
def make_trade_id(
    asset_type: str,
    transaction_type: str,
    lawd_cd: str,
    item: dict,
):
    """
    거래를 유일하게 식별하는 fingerprint 생성
    - 서비스 기준(asset_type)
    - 거래 유형(transaction_type)
    - 지역(lawd_cd)
    - 거래 고유 정보
    """

    seq = (
        item.get("aptSeq")
        or item.get("houseSeq")
        or item.get("offiSeq")
        or item.get("buildSeq")
        or "UNKNOWN"
    )

    deal_date = (
        f"{item.get('dealYear')}"
        f"{int(item.get('dealMonth')):02d}"
        f"{int(item.get('dealDay')):02d}"
    )

    return "|".join([
        asset_type,                 # HOUSE / APARTMENT / OFFICETEL
        transaction_type,           # TRADE / RENT
        lawd_cd,
        str(seq),
        deal_date,
        str(item.get("floor", "")),
        str(item.get("excluUseAr", "")),
    ])


# 데이터 해시 생성
def make_hash(item: dict):
    normalized = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

# 오늘 기준 최근 n개월 리스트 생성
def get_recent_months(n: int):
    today = datetime.today()
    result = []

    for i in range(n):
        y = today.year
        m = today.month - i
        if m <= 0:
            y -= 1
            m += 12
        result.append(f"{y}{m:02d}")

    return result

# ======================
# ======================
# ======================
# ======================
# ======================

from state.postgres import init_table, get_trade_hash, upsert_trade
from messaging.producer import KafkaEventProducer

# fetchers
from fetchers.apartment_trade import fetch_apartment_trade_month
from fetchers.apartment_rent import fetch_apartment_rent_month
from fetchers.officetel_trade import fetch_officetel_trade_month
from fetchers.officetel_rent import fetch_officetel_rent_month
from fetchers.house_single_trade import fetch_house_single_trade_month
from fetchers.house_multi_trade import fetch_house_multi_trade_month
from fetchers.house_multi_rent import fetch_house_multi_rent_month

# ======================
# 설정
# ======================
LAW_CODES = ["11110"]  # 테스트용
FETCH_JOBS = [
    ("APARTMENT", "TRADE", fetch_apartment_trade_month),
    ("APARTMENT", "RENT", fetch_apartment_rent_month),
    ("OFFICETEL", "TRADE", fetch_officetel_trade_month),
    ("OFFICETEL", "RENT", fetch_officetel_rent_month),
    ("HOUSE", "TRADE", fetch_house_single_trade_month),
    ("HOUSE", "TRADE", fetch_house_multi_trade_month),
    ("HOUSE", "RENT", fetch_house_multi_rent_month),
    ("COMMERCIAL", "TRADE", fetch_officetel_trade_month),  # 상업용은 오피스텔 API 재사용
]

# ======================
# main 함수
# ======================
def main():
    """
    main 함수의 책임

    1. 수집 대상 범위 결정 (지역, 기간)
    2. API 호출 (fetchers)
    3. 거래 fingerprint 기반 변경 감지 (Postgres)
    4. 변경된 데이터만 Kafka 이벤트로 전송
    """

    # ======================
    # 0. 상태 테이블 보장
    # ======================
    init_table()

    # Kafka Producer는 main 실행 동안 1개만 사용
    producer = KafkaEventProducer()

    # 최근 N개월 (예: 3개월)
    deal_ymds = get_recent_months(3)

    # ======================
    # 1. API × 지역 × 기간 루프
    # ======================
    for asset_type, txn_type, fetcher in FETCH_JOBS:
        for lawd_cd in LAW_CODES:
            for deal_ymd in deal_ymds:
                print(f"[START] {asset_type} {txn_type} {lawd_cd} {deal_ymd}")

                # ----------------------
                # 1-1. API 호출
                # ----------------------
                try:
                    items = fetcher(lawd_cd, deal_ymd)
                except Exception as e:
                    # fetch 실패는 전체 파이프라인을 멈추지 않음
                    print(f"[FETCH ERROR] {asset_type} {txn_type} {e}")
                    continue

                # ----------------------
                # 1-2. 거래 단위 처리
                # ----------------------
                for item in items:
                    # 거래를 유일하게 식별하는 ID
                    trade_id = make_trade_id(
                        asset_type, 
                        txn_type,
                        lawd_cd, 
                        item)

                    # 현재 데이터의 hash (변경 감지용)
                    data_hash = make_hash(item)

                    # 이전 실행에서 저장된 hash 조회
                    prev_hash = get_trade_hash(trade_id)

                    # ======================
                    # 신규 거래
                    # ======================
                    if prev_hash is None:
                        producer.send_event(
                            event_type="CREATE",
                            asset_type=asset_type,
                            transaction_type=txn_type,
                            fingerprint=trade_id,
                            lawd_cd=lawd_cd,
                            deal_ymd=deal_ymd,
                            payload=item,
                        )

                        # 상태 저장
                        upsert_trade(
                            trade_id,
                            asset_type,
                            txn_type,
                            lawd_cd,
                            deal_ymd,
                            data_hash,
                        )

                    # ======================
                    # 변경 거래
                    # ======================
                    elif prev_hash != data_hash:
                        producer.send_event(
                            event_type="UPDATE",
                            asset_type=asset_type,
                            transaction_type=txn_type,
                            fingerprint=trade_id,
                            lawd_cd=lawd_cd,
                            deal_ymd=deal_ymd,
                            payload=item,
                        )

                        # 상태 갱신
                        upsert_trade(
                            trade_id,
                            asset_type,
                            txn_type,
                            lawd_cd,
                            deal_ymd,
                            data_hash,
                        )

                    # 변경 없는 경우는 아무 것도 안 함

                print(f"[DONE] {asset_type} {txn_type} {lawd_cd} {deal_ymd}")

    # ======================
    # 2. Kafka flush
    # ======================
    # main 실행이 끝나기 전에
    # 버퍼에 남은 이벤트를 전부 전송
    producer.flush()


if __name__ == "__main__":
    main()


# =====================
# kafka 임시 강제 실행 명령어
# bash창에 복사해서 붙여넣기
# =====================

# 최초 토픽 생성
'''
docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.apartment   --partitions 1 --replication-factor 1 || true
docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.house       --partitions 1 --replication-factor 1 || true
docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.officetel   --partitions 1 --replication-factor 1 || true
docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.commercial  --partitions 1 --replication-factor 1 || true
# 확인
docker exec kafka kafka-topics --bootstrap-server kafka:9092 --list
'''
# docker exec -it kafka_producer python /app/main.py

# 토픽 목록
# docker exec -it kafka kafka-topics --bootstrap-server kafka:9092 --list

# 특정 토픽 메시지 확인
'''
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic realestate.apartment \
  --from-beginning
'''