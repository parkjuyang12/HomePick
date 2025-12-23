from django.urls import path
from . import views

urlpatterns = [
    # 프론트엔드에 API 키 전달
    path('config/', views.MapConfigView.as_view(), name='map-config'),

    # 주소 -> 좌표 변환 (Geocoding)
    path('geocode/', views.GeocodeView.as_view(), name='map-geocode'),
]
