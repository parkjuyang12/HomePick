"""
Kafka Topic을 미리 생성하는 스크립트
main.py 실행 전에 먼저 실행
"""
import time
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError

# ======================
# 설정
# ======================
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'zigbang-listings-raw'

# ======================
# Helper Functions
# ======================
def wait_for_kafka(max_retries=20, delay=3):
    """Kafka 준비 상태 대기"""
    print(f"[WAIT] Checking Kafka status... (Max {max_retries * delay}s)")
    
    for attempt in range(max_retries):
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=[BOOTSTRAP_SERVERS],
                client_id='health-check',
                request_timeout_ms=3000
            )
            admin_client.close()
            print(f"[OK] Kafka is ready (Attempt {attempt + 1}/{max_retries})")
            return True
        except Exception as e:
            error_msg = str(e)[:80]
            print(f"[RETRY] Waiting... ({attempt + 1}/{max_retries}) - {error_msg}")
            time.sleep(delay)
    
    return False

# ======================
# Main
# ======================
def create_kafka_topic():
    """Topic 생성 및 확인"""
    try:
        if not wait_for_kafka():
            print("[FATAL] Kafka is not reachable")
            return False
        
        print(f"[INFO] Connecting to AdminClient ({BOOTSTRAP_SERVERS})")
        admin_client = KafkaAdminClient(
            bootstrap_servers=[BOOTSTRAP_SERVERS],
            client_id='topic-creator',
            request_timeout_ms=10000
        )
        
        existing_topics = admin_client.list_topics()
        print(f"[INFO] Existing topics: {list(existing_topics)}")
        
        if TOPIC_NAME in existing_topics:
            print(f"[SKIP] Topic '{TOPIC_NAME}' already exists")
        else:
            print(f"[CREATE] Creating topic '{TOPIC_NAME}'...")
            topic = NewTopic(
                name=TOPIC_NAME,
                num_partitions=3,
                replication_factor=1
            )
            admin_client.create_topics([topic], validate_only=False)
            print(f"[DONE] Topic '{TOPIC_NAME}' created")
        
        admin_client.close()
        print("[EXIT] Setup completed successfully")
        return True
        
    except TopicAlreadyExistsError:
        print(f"[SKIP] Topic '{TOPIC_NAME}' already exists (Concurrent)")
        return True
    except KafkaError as e:
        print(f"[ERROR] Kafka Error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = create_kafka_topic()
    exit(0 if success else 1)