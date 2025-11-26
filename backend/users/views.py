from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny  # ✅ 추가
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.conf import settings
from allauth.socialaccount.models import SocialAccount
import requests
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class KakaoCallbackView(APIView):
    """
    카카오 OAuth 콜백 처리
    - 인증 코드 받기
    - 토큰 교환
    - 사용자 정보 가져오기
    - DB에 사용자 생성/업데이트
    - Django 토큰 발급
    """
    permission_classes = [AllowAny]  # ✅ 누구나 접근 가능
    
    def get(self, request):
        code = request.GET.get('code')
        
        if not code:
            return Response(
                {'error': '인증 코드가 제공되지 않았습니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 1. 카카오 액세스 토큰 받기
            kakao_token_data = self.get_kakao_token(code)
            kakao_access_token = kakao_token_data.get('access_token')
            
            if not kakao_access_token:
                logger.error(f"카카오 토큰 응답: {kakao_token_data}")
                return Response(
                    {'error': '카카오 토큰을 받는데 실패했습니다.', 'details': kakao_token_data}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. 카카오 사용자 정보 받기
            kakao_user_info = self.get_kakao_user_info(kakao_access_token)
            logger.info(f"카카오 사용자 정보: {kakao_user_info}")
            
            # 3. 사용자 생성 또는 업데이트
            user, created = self.get_or_create_user(kakao_user_info)
            
            # 4. Django 토큰 생성
            django_token, _ = Token.objects.get_or_create(user=user)
            
            logger.info(f"로그인 성공 - User: {user.username}, 신규: {created}")
            
            # 5. 프론트엔드로 리다이렉트
            frontend_url = (
                f"{settings.FRONTEND_URL}/auth/kakao/callback"
                f"?token={django_token.key}"
                f"&user_id={user.id}"
                f"&is_new_user={'true' if created else 'false'}"
            )
            
            return redirect(frontend_url)
            
        except Exception as e:
            logger.error(f"카카오 로그인 오류: {str(e)}", exc_info=True)
            return Response(
                {'error': '로그인 처리 중 오류가 발생했습니다.', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_kakao_token(self, code):
        """카카오 액세스 토큰 받기"""
        token_url = 'https://kauth.kakao.com/oauth/token'
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_REST_API_KEY,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'code': code,
        }
        
        response = requests.post(token_url, data=data)
        return response.json()
    
    def get_kakao_user_info(self, access_token):
        """카카오 사용자 정보 가져오기"""
        user_info_url = 'https://kapi.kakao.com/v2/user/me'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        response = requests.get(user_info_url, headers=headers)
        return response.json()
    
    def get_or_create_user(self, kakao_user_info):
        """
        카카오 정보로 사용자 생성 또는 가져오기
        """
        kakao_id = str(kakao_user_info.get('id'))
        kakao_account = kakao_user_info.get('kakao_account', {})
        profile = kakao_account.get('profile', {})
        
        # 카카오 정보 추출
        email = kakao_account.get('email', f'kakao_{kakao_id}@kakao.com')
        nickname = profile.get('nickname', f'사용자{kakao_id[:6]}')
        profile_image = profile.get('profile_image_url', '')
        
        # SocialAccount로 기존 사용자 찾기
        try:
            social_account = SocialAccount.objects.get(
                provider='kakao',
                uid=kakao_id
            )
            user = social_account.user
            created = False
            
            # 기존 사용자 정보 업데이트
            user.nickname = nickname
            user.profile_image = profile_image
            user.save()
            
            logger.info(f"기존 사용자 로그인: {user.username}")
            
        except SocialAccount.DoesNotExist:
            # 새 사용자 생성
            user = User.objects.create(
                username=f'kakao_{kakao_id}',
                email=email,
                nickname=nickname,
                profile_image=profile_image,
                kakao_id=kakao_id,
            )
            
            # SocialAccount 생성
            SocialAccount.objects.create(
                user=user,
                provider='kakao',
                uid=kakao_id,
                extra_data=kakao_user_info
            )
            
            created = True
            logger.info(f"새 카카오 사용자 생성: {user.username}")
        
        return user, created


class UserInfoView(APIView):
    """
    현재 로그인한 사용자 정보 조회/수정
    """
    permission_classes = [AllowAny]  # ✅ 임시로 AllowAny (테스트용)
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': '인증이 필요합니다.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': '인증이 필요합니다.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        from .serializers import UserSerializer
        serializer = UserSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    """로그아웃 (토큰 삭제)"""
    
    def post(self, request):
        if request.user.is_authenticated:
            # 사용자의 토큰 삭제
            Token.objects.filter(user=request.user).delete()
            return Response({'message': '로그아웃 되었습니다.'})
        
        return Response(
            {'error': '인증이 필요합니다.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )