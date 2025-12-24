from django.urls import path
from . import views
from .views import search_nearby_properties

urlpatterns = [
    # 프론트엔드에 API 키 전달
    path('config/', views.MapConfigView.as_view(), name='map-config'),

    # 주소 -> 좌표 변환 (Geocoding)
    path('geocode/', views.GeocodeView.as_view(), name='map-geocode'),

    path('search/', search_nearby_properties, name='search_nearby'),
    
    # 건물별 상세조회
    path('properties/<str:property_id>/history/',
        views.PropertyHistoryView.as_view(),
        name='map-property-history'
    ),
]
