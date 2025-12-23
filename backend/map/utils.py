from django.conf import settings
import requests

class GoogleMapClient:
    """
        Google Maps API와 통신을 담당하는 클래스
    """
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    def get_lat_lng(self, address):
        """
            주소를 입력 받아 (위도, 경도) 튜플을 반환하는 함수
        """
        endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key,
            "language": "ko"
        }

        response = requests.get(endpoint, params=params)
        data = response.json()

        # 구글 API 응답 상태 확인
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            return None, None
    