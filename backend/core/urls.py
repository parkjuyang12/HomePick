from django.contrib import admin
from django.urls import path, include

"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('api/v1/auth/', include('rest_auth.urls')),          # 로그인, 로그아웃
    path('api/v1/auth/registration/', include('rest_auth.registration.urls')), # 회원가입
    path('api/v1/auth/social/', include('allauth.socialaccount.urls')), # 카카오 로그인 처리
    path('api/v1/apartment/', include('apartment.urls')), # 부동산 데이터 API
]