from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 카카오 로그인 콜백
    path('kakao/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'),
    
    # 사용자 정보 조회/수정
    path('me/', views.UserInfoView.as_view(), name='user_info'),
    
    # 로그아웃
    path('logout/', views.LogoutView.as_view(), name='logout'),
]