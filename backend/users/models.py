from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 기본 정보
    nickname = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="닉네임"
    )
    
    profile_image = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="프로필 이미지"
    )
    
    # 소셜 로그인 관련
    kakao_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name="카카오 ID"
    )
    
    # 추가 정보
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,  
        verbose_name="전화번호"
    )
    
    birth_date = models.DateField(
        null=True,  
        blank=True, 
        verbose_name="생년월일"
    )
    
    # 타임스탬프
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="가입일"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="수정일"
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
    
    def __str__(self):
        return f"{self.username} ({self.nickname or self.email})"