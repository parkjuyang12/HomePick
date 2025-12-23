from dotenv import load_dotenv
import os
import time
import requests
from typing import Optional
import logging

# ==================================================
# 목적
# ==================================================
# 이 스크립트는 Elasticsearch의 current 인덱스에 저장된 문서 중
# 'location(위도/경도)' 필드가 없는 문서를 찾아
# 카카오 지오코딩 API를 통해 좌표를 조회하고
# 해당 문서를 부분 업데이트(_update)하는 배치성 보강 파이프라인.
#
# ✔ Flink 스트리밍 파이프라인과 분리하여 실행
# ✔ 좌표 보강은 current 인덱스에만 수행
# ✔ 외부 API 호출 부담을 줄이기 위해 캐시 + 재시도 전략 적용
#
# → 실시간 처리(Flink)와 비실시간 보강 작업을 분리한 구조
# ==================================================

# ==================================================
# 환경 변수 로딩
# ==================================================
load_dotenv()

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# Elasticsearch 접속 정보 및 인덱스 패턴 (환경변수로 오버라이드 가능)
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX", "realestate_current_*")  # current 인덱스들(아파트/주택 등)

# 카카오 REST API 키 (Kakao Developers에서 발급)
KAKAO_API_KEY = os.getenv("KAKAO_MAPS_API_KEY")
if not KAKAO_API_KEY:
    raise RuntimeError("KAKAO_MAPS_API_KEY is not set")

# 한 번에 처리할 문서 수와 API 호출 간 슬립 (rate limit 보호)
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
SLEEP_SEC = float(os.getenv("SLEEP_SEC", "0.2"))

# HTTP 요청 헤더
ES_HEADERS = {"Content-Type": "application/json"}
KAKAO_HEADERS = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

# ==================================================
# 인메모리 캐시
# ==================================================
# 같은 실행(run) 중 동일한 주소에 대한 중복 API 호출 방지
# (ES 문서 수가 많을수록 API 비용 절감 효과 큼)
_geo_cache = {}

# ==================================================
# Kakao API 공통 요청 함수
# ==================================================
def _kakao_request(url: str, params: dict, retries: int = 3, backoff: float = 0.5):
    """
    카카오 API 호출을 담당하는 공통 함수
    - 네트워크 오류 / 5xx / rate limit 발생 시 재시도
    - exponential backoff 적용
    """
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=KAKAO_HEADERS, params=params, timeout=5)
            # 정상 응답
            if r.status_code == 200:
                return r.json()

            # 재시도 가능 상태 코드
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                sleep = backoff * (2 ** (attempt - 1))
                logging.warning(f"Kakao request status={r.status_code}, retrying in {sleep}s")
                time.sleep(sleep)
                continue

            # 재시도 불가능한 상태 
            logging.error(f"HTTP ERROR | status={r.status_code} | params={params}")
            try:
                logging.debug(r.text)
            except Exception:
                pass
            return None

        except Exception as e:
            if attempt < retries:
                sleep = backoff * (2 ** (attempt - 1))
                logging.warning(f"Kakao request exception: {e}, retrying in {sleep}s")
                time.sleep(sleep)
                continue
            logging.error(f"Kakao request failed: {e}")
            return None


# =============================================
# 단일 쿼리 지오코드 시도
# - use_keyword=False: 주소 전용 API(/address.json)를 사용 (도로명/지번에 적합)
# - use_keyword=True : 키워드 API(/keyword.json)를 사용 (건물/상호명 기반 검색에 적합)
# - 응답이 여러개일 수 있으므로 현재는 첫 문서(documents[0])를 활용한다.
#   필요시 후보들에 대한 추가 선별 로직을 도입할 수 있음.
# =============================================
def geocode_query(query: str, use_keyword: bool = False) -> Optional[dict]:
    cache_key = f"kw:{use_keyword}:{query}"
    if cache_key in _geo_cache:
        return _geo_cache[cache_key]

    if use_keyword:
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    else:
        url = "https://dapi.kakao.com/v2/local/search/address.json"

    params = {"query": query}
    data = _kakao_request(url, params)
    if not data:
        return None

    if not data.get("documents"):
        # no results
        return None

    doc = data["documents"][0]
    try:
        location = {"lat": float(doc["y"]), "lon": float(doc["x"])}
    except Exception:
        return None

    _geo_cache[cache_key] = location
    return location


# ===================================================
# 주소 필드 조합 기반의 재시도 로직
# - ES에 들어있는 다양한 주소 서브필드를 보고, 복수의 검색 쿼리 후보를 생성
# - 각 후보에 대해 주소 API 먼저 시도하고, 실패하면 키워드 API를 시도
# - 최종적으로 어느 후보도 못찾으면 None 반환
# ===================================================
def geocode_with_fallback(source: dict) -> Optional[dict]:
    """
    ES 문서의 address 필드를 활용해
    여러 형태의 검색 쿼리를 순차적으로 시도한다.

    우선순위 예:
    1) address.display
    2) 법정동 + 단지명
    3) 단지명 단독
    4) 법정동 + 지번

    각 쿼리에 대해:
    - 주소 API → 실패 시 키워드 API 순으로 시도
    """
    addr = source.get("address", {})
    display = addr.get("display")
    sgg = addr.get("sgg")
    umd = addr.get("umd")
    jibun = addr.get("jibun")

    apt_name = None
    building_name = None
    # nested checks for apartment/building names
    if isinstance(addr.get("apartment"), dict):
        apt_name = addr["apartment"].get("name")
    if isinstance(addr.get("building"), dict):
        building_name = addr["building"].get("name")

    candidates = []
    if display:
        # 사용자 표시용 전체 문자열은 우선 시도
        candidates.append((display, False))  # prefer address endpoint for display

    # sensible fallbacks: 단지/건물명, 법정동+번지 등
    if umd and apt_name:
        candidates.append((f"{umd} {apt_name}", True))
        candidates.append((apt_name, True))
    if sgg and building_name:
        candidates.append((f"{sgg} {building_name}", True))
        candidates.append((building_name, True))
    if umd and jibun:
        candidates.append((f"{umd} {jibun}", False))

    # deduplicate while preserving order
    seen = set()
    unique = []
    for q, use_kw in candidates:
        qn = q.strip()
        if not qn or qn in seen:
            continue
        seen.add(qn)
        unique.append((qn, use_kw))

    for q, use_kw in unique:
        # try address endpoint first if not using keyword
        loc = geocode_query(q, use_keyword=False)
        if loc:
            logging.info(f"geocode success (address) | q={q}")
            return loc
        # try keyword endpoint
        loc = geocode_query(q, use_keyword=True)
        if loc:
            logging.info(f"geocode success (keyword) | q={q}")
            return loc

    # nothing found
    logging.warning(f"NO DOCUMENTS (all variants) | display={display} candidates={ [q for q,_ in unique] }")
    return None

# ==================================================
# ES: location 없는 문서 조회
# ==================================================
# ES에서 좌표가 없는 문서들 조회
# - 추가적으로 address의 서브필드를 가져오며, 이 필드들을 기반으로
#   여러 후보 쿼리를 만들어 카카오에 질의합니다.
# - size는 BATCH_SIZE로 조절 (과도한 동시 호출 방지)
def fetch_targets():
    query = {
        "size": BATCH_SIZE,
        "_source": [
            "address.display",
            "address.umd",
            "address.sgg",
            "address.jibun",
            "address.apartment",
            "address.building",
        ],
        "query": {
            "bool": {
                "must_not": {
                    "exists": {"field": "location"}
                }
            }
        }
    }

    r = requests.post(
        f"{ES_HOST}/{ES_INDEX}/_search",
        headers=ES_HEADERS,
        json=query,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["hits"]["hits"]


# ==================================================
# ES: 부분 업데이트
# ==================================================
# ES 문서 부분 갱신 함수
# - location: {lat, lon} 형태로 부분(doc) 업데이트
# - 단순한 HTTP POST를 사용하며 실패 시 예외가 발생하도록 r.raise_for_status()
def update_location(index: str, doc_id: str, location: dict):
    body = {
        "doc": {
            "location": location
        }
    }

    r = requests.post(
        f"{ES_HOST}/{index}/_update/{doc_id}",
        headers=ES_HEADERS,
        json=body,
        timeout=5,
    )
    r.raise_for_status()

# ==================================================
# main
# ==================================================
def main():
    logging.info("geo-enricher started")

    while True:
        hits = fetch_targets() # location 없는 문서 조회
        if not hits:
            logging.info("no more documents to enrich")
            break

        for hit in hits:
            index = hit["_index"]
            doc_id = hit["_id"]
            src = hit["_source"]
            address_display = src.get("address", {}).get("display")

            if not address_display:
                logging.warning(f"skipping doc without display | {doc_id}")
                continue

            location = geocode_with_fallback(src)
            if not location:
                logging.warning(f"geocode failed: {address_display}")
                continue

            try:
                update_location(index, doc_id, location)
                logging.info(f"updated {doc_id} -> {location}")
            except Exception as e:
                logging.error(f"update failed: {doc_id} error={e}")

            time.sleep(SLEEP_SEC)

if __name__ == "__main__":
    main()
