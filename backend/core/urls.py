from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # dj-rest-auth (기본 인증)
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # users 앱 (카카오 로그인 등)
    path('api/v1/auth/social/login/', include('users.urls')),
    
    # allauth
    path('accounts/', include('allauth.urls')),
]