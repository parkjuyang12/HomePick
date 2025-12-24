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
            - 좌표 형태("lat,lng")인 경우: 바로 파싱하여 반환
            - 주소 문자열인 경우: Google Geocoding API 호출
        """
        # 좌표 형태인지 확인 (예: "37.1234,127.5678")
        if ',' in address:
            try:
                parts = address.split(',')
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    # 유효한 좌표 범위 확인
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        return lat, lng
            except ValueError:
                pass  # 숫자 변환 실패 시 일반 주소로 처리

        # 일반 주소 문자열 처리
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
    