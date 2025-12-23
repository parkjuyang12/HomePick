import requests
import time

class ZigbangFetcher:
    def __init__(self):
        self.base_url = "https://apis.zigbang.com/apt/locals/{}/item-catalogs"
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "origin": "https://www.zigbang.com",
            "referer": "https://www.zigbang.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "x-zigbang-platform": "www"
        }

    def fetch_listings_by_bcode(self, bcode):
        offset = 0
        limit = 20
        
        params = {
            "tranTypeIn[0]": "trade",
            "tranTypeIn[1]": "charter",
            "tranTypeIn[2]": "rental",
            "includeOfferItem": "true",
            "offset": offset,
            "limit": limit
        }

        target_url = self.base_url.format(bcode)
        try:
            # response = requests.get(target_url, headers=self.headers, params=params)
            try:
                response = requests.get(target_url, headers=self.headers, params=params, timeout=5)
                # ... (이하 동일)
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout: {target_url} 응답이 너무 늦습니다.")
                return []
            except Exception as e:
                print(f"Request Error: {e}")
                return []
            if response.status_code == 200:
                data = response.json()
                items = data.get("list", [])
                return items if items else []
            return []
        except Exception as e:
            print(f"Request Error: {e}")
            return []