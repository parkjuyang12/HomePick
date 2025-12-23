import json
from kafka import KafkaConsumer

# ======================
# 설정
# ======================
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'zigbang-listings-raw'
GROUP_ID = 'zigbang-consumer-group-02'

# ======================
# Main
# ======================
def run_consumer():
    # 1. Consumer 초기화
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[BOOTSTRAP_SERVERS],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        api_version=(2, 5, 0)
    )

    print(f"[START] Connected to {BOOTSTRAP_SERVERS}. Listening on {TOPIC_NAME}...")

    # 2. 메시지 수신 루프
    try:
        for message in consumer:
            data = message.value
            
            # 데이터 식별 정보 추출
            loc = f"{data.get('local2', '')} {data.get('local3', '')}"
            title = data.get('itemTitle', 'No Title')

            print(f"[RECV] {loc} - {title}")
            
            # TODO: DB 저장 로직 구현 (psycopg2 등)

    except KeyboardInterrupt:
        print("[STOP] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] Consumer error: {e}")
    finally:
        consumer.close()
        print("[EXIT] Consumer closed")

if __name__ == "__main__":
    run_consumer()