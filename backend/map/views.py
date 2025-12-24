from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.http import JsonResponse
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Radians, Sin
from elasticsearch import Elasticsearch
from .utils import GoogleMapClient
from properties.services.history import format_deal_date, normalize_price

es = Elasticsearch("http://elasticsearch:9200")

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
    radius = float(request.GET.get('radius', 2))

    # utils.py를 사용하여 주소를 좌표로 변환
    client = GoogleMapClient()
    lat, lng = client.get_lat_lng(address)

    # Haversine 공식을 이용한 DB 쿼리 필터링 (6371은 지구 반지름 km)
    distance_formula = 6371 * ACos(
        Cos(Radians(lat)) * Cos(Radians(F('lat'))) *
        Cos(Radians(F('lng')) - Radians(lng)) +
        Sin(Radians(lat)) * Sin(Radians(F('lat')))
    )

    # 반경 내 매물 필터링
    nearby_list = Property.objects.annotate(
        distance=ExpressionWrapper(distance_formula, output_field=FloatField())
    ).filter(distance__lte=radius).order_by('distance')

    # 결과 반환
    results = [
        {
            'id': p.id,
            'title': p.title,
            'lat': p.lat,
            'lng': p.lng,
            'distance': round(p.distance, 2)
        } for p in nearby_list
    ]

    return JsonResponse({
        'center': {'lat': lat, 'lng': lng},
        'results': results
    })


class PropertyHistoryView(APIView):
    """
    마커 클릭 → property_id 기준 거래 이력 조회
    """

    def get(self, request, property_id):
        query = {
            "size": 1000,
            "query": {
                "term": {
                    "property_id": property_id
                }
            },
            "sort": [
                {"deal_date": "desc"}
            ]
        }

        res = es.search(index="realestate_history", body=query)
        rows = [hit["_source"] for hit in res["hits"]["hits"]]

        history = []
        for row in rows:
            detail = row.get("detail", {})

            history.append({
                "deal_date": format_deal_date(row.get("deal_date")),
                "transaction_type": row.get("transaction_type"),
                "price": normalize_price(row),

                "spec": {
                    "area": detail.get("area"),
                    "floor": detail.get("floor"),
                },

                "meta": {
                    "buyer_type": detail.get("buyer_type"),
                    "seller_type": detail.get("sler_type"),
                    "deal_method": detail.get("deal_method"),
                }
            })
