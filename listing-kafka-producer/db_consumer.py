import json
import os
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

# ======================
# 설정
# ======================
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': 'localhost',
    'port': '5432'
}

KAFKA_CONFIG = {
    'bootstrap_servers': ['localhost:9092'],
    'auto_offset_reset': 'latest',  # 실시간 적재용
    'enable_auto_commit': True,
    'group_id': 'zigbang-db-writer-group',
    'value_deserializer': lambda x: json.loads(x.decode('utf-8')),
    'api_version': (2, 5, 0)
}

TOPIC_NAME = 'zigbang-listings-raw'

INSERT_SQL = """
    INSERT INTO listings 
    (item_id, area_ho_id, title, address_local2, address_local3, lat, lng, deposit, rent)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (item_id) 
    DO UPDATE SET
        title = EXCLUDED.title,
        deposit = EXCLUDED.deposit,
        rent = EXCLUDED.rent,
        lat = EXCLUDED.lat,
        lng = EXCLUDED.lng;
"""

# ======================
# Main
# ======================
def run_db_consumer():
    # 1. Consumer 초기화
    consumer = KafkaConsumer(TOPIC_NAME, **KAFKA_CONFIG)
    print(f"[START] Kafka Consumer connected to {TOPIC_NAME}")

    conn = None
    try:
        # 2. DB 연결
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("[INFO] PostgreSQL Connected")

        # 3. 데이터 처리 루프
        for message in consumer:
            data = message.value

            # 필드 추출 (Default 값 처리 포함)
            item_id = str(data.get('itemIdList', [{}])[0].get('itemId', '0'))
            area_ho_id = str(data.get('areaHoId', '0'))
            title = data.get('itemTitle', 'No Title')
            local2 = data.get('local2', '')
            local3 = data.get('local3', '')
            lat = data.get('lat', 0.0)
            lng = data.get('lng', 0.0)
            deposit = data.get('depositMin', 0)
            rent = data.get('rentMin', 0)

            try:
                cur.execute(INSERT_SQL, (item_id, area_ho_id, title, local2, local3, lat, lng, deposit, rent))
                conn.commit()

                # rowcount: 1(삽입 성공), 0(중복 무시)
                if cur.rowcount > 0:
                    print(f"[INSERT] {local3} - {title}")
                else:
                    print(f"[SKIP] Duplicate ID: {item_id}")

            except Exception as e:
                print(f"[ERROR] SQL Execution failed: {e}")
                conn.rollback()

    except KeyboardInterrupt:
        print("[STOP] Interrupted by user")
    except Exception as e:
        print(f"[FATAL] System Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("[EXIT] DB Connection closed")

if __name__ == "__main__":
    run_db_consumer()