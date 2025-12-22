import requests
import time
import logging
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    def __init__(self, producer_client):
        self.producer = producer_client
        self.base_url = "https://m.land.naver.com/cluster/ajax/articleList"
        # 네이버 차단 방지를 위한 필수 헤더 설정
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://m.land.naver.com/",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, cortarNo, rletTpCd, tradTpCd="A1:B1:B2"):
        """
        네이버 부동산 XHR 엔드포인트에서 데이터를 가져와 Kafka로 전송
        :cortarNo: 법정동 코드
        :rletTpCd: 매물 유형 (예: APT, OPST, VL)
        :tradTpCd: 거래 유형 (A1:매매, B1:전세, B2:월세)
        """
        page = 1
        while True:
            params = {
                "cortarNo": cortarNo,
                "rletTpCd": rletTpCd,
                "tradTpCd": tradTpCd,
                "z": "12",
                "lat": "37.5665", # 중심 좌표 (필요시 동적으로 변경)
                "lon": "126.9780",
                "order": "now",   # 최신순 정렬 (준실시간 핵심)
                "page": page
            }

            try:
                response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                articles = data.get('body', [])
                if not articles:
                    self.logger.info(f"더 이상 데이터가 없습니다. (Page: {page})")
                    break

                for article in articles:
                    self.send_to_kafka(article)

                # 페이지가 하나만 필요한 경우(준실시간 업데이트)는 break
                # 전체 데이터를 긁어야 하는 경우만 page += 1 유지
                if self._should_stop_after_first_page():
                    break
                
                page += 1
                time.sleep(1) # 차단 방지를 위한 짧은 지연

            except Exception as e:
                self.logger.error(f"Error fetching data: {e}")
                break

    def send_to_kafka(self, article):
        """Kafka 전송 로직 (Topic과 Key 설정)"""
        topic = "naver-property-raw"
        article_no = article.get('atclNo') # 매물 고유 번호
        self.producer.send(topic, key=article_no, value=article)

    def _should_stop_after_first_page(self):
        """준실시간 수집 시에는 최신 데이터가 포함된 1페이지만 확인하면 됩니다."""
        return True

    @abstractmethod
    def run(self):
        """자식 클래스에서 수집 대상 지역 코드 등을 정의하여 실행"""
        pass