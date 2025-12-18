import json
import os
from datetime import datetime
from kafka import KafkaProducer


class KafkaEventProducer:
    """
    Kafka로 '변경 이벤트'를 전송하는 Producer 클래스

    책임:
    - 이미 변경이라고 판단된 데이터를
    - 이벤트 형태로 Kafka topic에 전달만 한다
    """

    def __init__(self):
        # Kafka topic 공통 prefix
        # 실제 topic은: realestate.apartment, realestate.officetel ...
        self.topic_prefix = "realestate"

        # Kafka Producer 생성
        self.producer = KafkaProducer(
            # Kafka broker 주소
            # Docker compose 환경에서는 서비스 이름을 hostname으로 사용
            bootstrap_servers=os.getenv("KAFKA_BROKER", "kafka:9092"),

            # value(dict)를 JSON 문자열로 직렬화 후 bytes로 변환
            # ensure_ascii=False → 한글(아파트명 등) 깨짐 방지
            value_serializer=lambda v: json.dumps(
                v, ensure_ascii=False
            ).encode("utf-8"),

            # key는 문자열 → bytes 변환
            # 우리는 trade_fingerprint를 key로 사용
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )

    def send_event(
        self,
        *,
        event_type: str,          # CREATE | UPDATE
        asset_type: str,          # APARTMENT | HOUSE | OFFICETEL | COMMERCIAL
        transaction_type: str,    # TRADE | RENT
        fingerprint: str,         # trade_id (Kafka key)
        lawd_cd: str,
        deal_ymd: str,
        payload: dict,
    ):
        """
        Kafka로 단일 이벤트를 전송한다.

        asset_type: APARTMENT / OFFICETEL / COMMERCIAL / HOUSE
        transaction_type: TRADE / RENT
        fingerprint: 거래를 유일하게 식별하는 값 (Kafka key)
        lawd_cd: 법정동 코드
        deal_ymd: 계약 연월
        payload: 실제 거래 데이터 (DB에 넣은 row 그대로)
        """

        # 서비스 기준 topic 결정
        # 예: realestate.apartment
        topic = f"{self.topic_prefix}.{asset_type.lower()}"

        # Kafka에 실릴 이벤트 메시지 구조
        event = {
            # 이벤트 종류
            "event_type": event_type,  # CREATE | UPDATE",
            
            # 자산 유형 (서비스/ES 분리 기준)
            "asset_type": asset_type,

            # 거래 유형 (매매/전월세)
            "transaction_type": transaction_type,

            # Kafka key로도 사용되는 fingerprint
            "fingerprint": fingerprint,

            # 지역 및 시점 정보
            "lawd_cd": lawd_cd,
            "deal_ymd": deal_ymd,

            # 실제 거래 데이터
            # 정제는 Flink/ES 단계에서 수행
            "payload": payload,

            # 이벤트 발생 시각 (UTC 기준)
            "occurred_at": datetime.utcnow().isoformat(),
        }

        # Kafka로 이벤트 전송
        # key를 fingerprint로 주면 같은 거래는 같은 partition으로 감
        self.producer.send(
            topic=topic,
            key=fingerprint,
            value=event,
        )

    def flush(self):
        """
        Producer 내부 버퍼에 남아 있는 메시지를
        Kafka로 강제 전송한다.

        - main 로직 마지막에서 한 번만 호출
        - send_event마다 호출하면 성능 나쁨
        """
        self.producer.flush()