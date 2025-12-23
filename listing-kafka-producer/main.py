import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from fetchers.zigbang_fetcher import ZigbangFetcher

# Kafka 설정
BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'zigbang-listings-raw'

# Helper 함수: Kafka Producer 생성
def create_producer():
    """
    Kafka Producer 생성 (재시도 로직 포함)
    """
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[BOOTSTRAP_SERVERS],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                api_version=(2, 5, 0), 
                acks=1,
                request_timeout_ms=5000  # 타임아웃 설정
            )
            print(f"[INFO] Kafka Producer Connected ({BOOTSTRAP_SERVERS})")
            return producer
        except NoBrokersAvailable:
            print(f"[RETRY] Kafka Connection ({retries + 1}/{max_retries})")
            retries += 1
            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Kafka Connection Unexpected: {e}")
            break
    return None

# Main Pipeline
def run_pipeline():
    # 1. Producer 초기화
    producer = create_producer()
    if producer is None:
        print("[FATAL] Kafka Producer init failed")
        return

    fetcher = ZigbangFetcher()
    
    # 2. 수집 대상 로드
    try:
        with open('bcodes_master.json', 'r', encoding='utf-8') as f:
            region_list = json.load(f)
    except FileNotFoundError:
        print("[FATAL] 'bcodes_master.json' file not found")
        return

    print(f"[INFO] Start collecting for {len(region_list)} regions")

    total_sent = 0
    total_errors = 0

    # 3. 지역별 순회 수집
    for idx, region in enumerate(region_list, 1):
        original_bcode = str(region['bcode'])
        fetch_code = original_bcode[:5] 
        region_name = region['name']

        print(f"[START] [{idx}/{len(region_list)}] {region_name} ({fetch_code})")

        try:
            # API 호출
            items = fetcher.fetch_listings_by_bcode(fetch_code)
            print(f"[FETCH] Count: {len(items)}")

            # Kafka 전송
            local_sent = 0
            for item in items:
                try:
                    # key 생성 (areaHoId 없으면 itemId 사용)
                    item_key = str(item.get('areaHoId') or item.get('itemIdList', [{}])[0].get('itemId'))
                    
                    producer.send(
                        topic=TOPIC_NAME,
                        key=item_key,
                        value=item
                    )
                    total_sent += 1
                except Exception as e:
                    total_errors += 1

            print(f"[DONE] Sent: {local_sent}")            
            
            # 진행 상황 주기적 로딩
            if idx % 50 == 0:
                print(f"[STAT] Total Sent: {total_sent}, Total Errors: {total_errors}")
            
            time.sleep(0.3)

        except KeyboardInterrupt:
            print("[STOP] Interrupted by user")
            break
        except Exception as e:
            print(f"[ERROR] Processing failed for {region_name}: {e}")
            total_errors += 1
            continue

    # 4. 종료 처리
    print("[FLUSH] Sending remaining messages...")
    producer.flush()
    producer.close()
    
    print(f"[EXIT] Finished. Success: {total_sent}, Failed: {total_errors}")

if __name__ == "__main__":
    run_pipeline()