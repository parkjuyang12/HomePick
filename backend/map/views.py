from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from .utils import GoogleMapClient

class MapConfigView(APIView):
    """
    [GET] /api/map/config/
    프론트엔드에서 사용할 Google Maps API Key 반환
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        api_key = settings.GOOGLE_MAPS_API_KEY
        return Response({"api_key": api_key}, status=status.HTTP_200_OK)

class GeocodeView(APIView):
    """
    [POST] /api/map/geocode/
    주소(address)를 받아 위도/경도를 반환
    """
    permission_classes = [AllowAny]

    def post(self, request):
        address = request.data.get('address')

        # 클라이언트 생성 및 좌표 변환 요청
        client = GoogleMapClient()
        lat, lng = client.get_lat_lng(address)

        return Response({
            "address": address,
            "lat": lat,
            "lng": lng
        }, status=status.HTTP_200_OK)
