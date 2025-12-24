from elasticsearch import Elasticsearch
import os

ES_HOST = os.environ.get("ELASTICSEARCH_HOST", "http://elasticsearch:9200")

class ESPropertyClient():
    def __init__(self):
        self.client = Elasticsearch(ES_HOST)

    def search_nearby(self, lat, lng, radius_km=2, category=None):
        """
        - lat, lng: 검색어 중심 좌표
        - radius_km: 검색 반경 (km)
        - category: 특정 인덱스(아파트/상가/...)만 검색할 때 사용
            1. 전체 불러오기: category=None일 때
            2. 인덱스별 불러오기: category='apartment' 등 값이 있을 때
        """
        index_name = category if category else "realestate_current_*"

        query = {
            "query": {
                "bool": {
                    "filter": {
                        "geo_distance": {
                            "distance": f"{radius_km}km",
                            "location": {"lat": lat, "lon": lng}
                        }
                    }
                }
            },
            "size": 1000
        }

        response = self.client.search(index=index_name, body=query, size=500)
        return response['hits']['hits']