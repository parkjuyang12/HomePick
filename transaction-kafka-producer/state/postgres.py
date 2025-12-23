import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# 테이블 없으면 생성
def init_table():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trade_fingerprint (
                    trade_id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    lawd_cd TEXT NOT NULL,
                    deal_ymd TEXT NOT NULL,
                    data_hash TEXT NOT NULL,
                    first_seen_at TIMESTAMP NOT NULL DEFAULT now(),
                    last_seen_at TIMESTAMP NOT NULL DEFAULT now()
                );
            """)
        conn.commit()



# trade_id로 기존 해시 조회(신규/변경/유지 확인)
def get_trade_hash(trade_id: str):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT data_hash FROM trade_fingerprint WHERE trade_id = %s",
                (trade_id,)
            )
            row = cur.fetchone()
            return row["data_hash"] if row else None

# 해시값 = 데이터 전체를 해시한 값
# 거래 상태 저장
def upsert_trade(
    trade_id,
    asset_type,
    transaction_type,
    lawd_cd,
    deal_ymd,
    data_hash,
):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO trade_fingerprint (
                    trade_id,
                    asset_type,
                    transaction_type,
                    lawd_cd,
                    deal_ymd,
                    data_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (trade_id)
                DO UPDATE SET
                    data_hash = EXCLUDED.data_hash,
                    last_seen_at = now();
            """, (
                trade_id,
                asset_type,
                transaction_type,
                lawd_cd,
                deal_ymd,
                data_hash,
            ))
        conn.commit()
