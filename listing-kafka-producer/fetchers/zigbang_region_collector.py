import requests
import json
import time

class ZigbangBcodeMasterCollector:
    def __init__(self):
        self.base_url = "https://apis.zigbang.com/apt/locals/prices/on-locals"
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "origin": "https://www.zigbang.com",
            "referer": "https://www.zigbang.com/",
            "x-zigbang-platform": "www"
        }
        # 서울과 경기도 전역을 커버하는 핵심 Geohash 리스트
        self.geohashes = [
            "wydm", "wydq", "wydp", "wydn", "wydr", "wydt", 
            "wydu", "wyds", "wyde", "wydg", "wyd7", "wyd6"
        ]

    def collect(self):
        all_bcodes = {} # 중복 제거를 위해 dict 사용
        
        print(f"🚀 서울/경기 BCODE 전체 수집 시작 (총 {len(self.geohashes)}개 구역)")
        
        for gh in self.geohashes:
            print(f"📡 구역 [{gh}] 데이터 요청 중...", end="\r")
            params = {
                "geohash": gh,
                "localLevel": 3, # '동' 단위까지 가져오기 위한 설정
                "comparingPeriod": 1
            }
            
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json().get('datas', [])
                    for item in data:
                        # 서울(11)과 경기(41) 법정동코드로 시작하는 데이터만 필터링
                        local_cd = item.get('localCd', '')
                        if local_cd.startswith(('11', '41')):
                            all_bcodes[local_cd] = {
                                "bcode": local_cd,
                                "name": item.get('address'),
                                "lat": item.get('lat'),
                                "lng": item.get('lng')
                            }
                time.sleep(0.5) # 서버 부하 방지
            except Exception as e:
                print(f"\n❌ 구역 [{gh}] 수집 중 에러 발생: {e}")

        result_list = list(all_bcodes.values())
        print(f"\n✨ 수집 완료! 총 {len(result_list)}개의 '동' 단위를 확보했습니다.")
        return result_list

if __name__ == "__main__":
    collector = ZigbangBcodeMasterCollector()
    master_list = collector.collect()
    
    # 결과를 JSON 파일로 저장
    with open('bcodes_master.json', 'w', encoding='utf-8') as f:
        json.dump(master_list, f, ensure_ascii=False, indent=4)
    
    print(f"💾 'bcodes_master.json' 파일이 생성되었습니다.")