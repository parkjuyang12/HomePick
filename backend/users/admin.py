from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'nickname', 'kakao_id', 'created_at', 'is_active']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'nickname', 'kakao_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('nickname', 'profile_image', 'kakao_id', 'phone_number', 'birth_date')
        }),
    )