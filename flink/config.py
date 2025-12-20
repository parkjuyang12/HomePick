# Kafka
# - 브로커 위치, 소비할 토픽, 컨슈머 그룹
KAFKA_BROKERS = "kafka:9092"
KAFKA_TOPICS = [
    "realestate.apartment",
    "realestate.house",
    "realestate.officetel",
    "realestate.commercial",
]
KAFKA_GROUP_ID = "realestate-flink"

# Elasticsearch
ES_HOST = "http://elasticsearch:9200"  # REST 엔드포인트

# 인덱스 네이밍 규칙
CURRENT_INDEX_PREFIX = "realestate_current"  # asset_type 소문자와 조합
HISTORY_INDEX = "realestate_history"        # 단일 append-only 인덱스
