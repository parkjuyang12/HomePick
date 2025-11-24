from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'nickname',
            'profile_image',
            'phone_number',
            'birth_date',
            'created_at',
        ]
        read_only_fields = ['id', 'username', 'created_at']


class KakaoUserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kakao_account = serializers.DictField()
    properties = serializers.DictField(required=False)