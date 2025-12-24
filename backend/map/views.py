# map/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.http import JsonResponse
from properties.utils import ESPropertyClient
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

def search_nearby_properties(request):
    address = request.GET.get('address')
    category = request.GET.get('category')
    if not address:
        return JsonResponse({'error': 'Address parameter is required.'}, status=400)
    # utils.py를 사용하여 주소를 좌표로 변환
    geo_client = GoogleMapClient()
    lat, lng = geo_client.get_lat_lng(address)

    if lat is None or lng is None:
        return JsonResponse({'error': 'Failed to geocode address.'}, status=400)

    # ES에서 데이터 가져오기
    es_client = ESPropertyClient()
    hits = es_client.search_nearby(lat, lng, radius_km=2, category=category)

    # 프론트엔드용 마커 데이터 가공
    results = []
    for hit in hits:
        source = hit['_source']
        results.append({
            'id': hit['_id'],
            'title': source.get('address', {}).get('display'),
            'lat': source.get('location', {}).get('lat'),
            'lng': source.get('location', {}).get('lon'),
            'price': source.get('latest_trade', {}).get('price'),
            'asset_type': source.get('asset_type'), # Apartment/House/Commercial/Officetel
            'transaction_type': source.get('latest_trade', {}).get('transaction_type'), # 매매/전세/월세
            'index': hit['_index'] # 아이콘 구분용
        })

    return JsonResponse({
        'center': {'lat': lat, 'lng': lng},
        'results': results
    })
