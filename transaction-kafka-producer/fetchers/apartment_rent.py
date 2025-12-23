import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"


def fetch_apartment_rent_month(
    lawd_cd: str,
    deal_ymd: str,
    num_of_rows: int = 1000,
) -> list[dict]:
    service_key = os.getenv("API_KEY")
    if not service_key:
        raise RuntimeError("API_KEY not set")

    page_no = 1
    results: list[dict] = []

    while True:
        url = (
            f"{BASE_URL}"
            f"?serviceKey={service_key}"
            f"&LAWD_CD={lawd_cd}"
            f"&DEAL_YMD={deal_ymd}"
            f"&pageNo={page_no}"
            f"&numOfRows={num_of_rows}"
            f"&_type=json"
        )

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        body = resp.json()["response"]["body"]
        items = body.get("items", {}).get("item", [])

        if not items:
            break

        if isinstance(items, dict):
            items = [items]

        results.extend(items)

        total_count = int(body["totalCount"])
        if page_no * num_of_rows >= total_count:
            break

        page_no += 1

    return results


### 호출 샘플
if __name__ == "__main__":
    data = fetch_apartment_rent_month(
        lawd_cd="11110",
        deal_ymd="202407",
    )

    print(f"count: {len(data)}")
    print(data[0])