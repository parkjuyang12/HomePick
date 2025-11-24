import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$5xa9hgp_*zpf3%ndn%#04qjv7w^^#k4xmyn20%kltkgri^$&9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 🚨 수정: 개발 환경에서 모든 호스트를 허용하여 경고를 제거합니다.
ALLOWED_HOSTS = ['*'] 

# ====================================================================
# 인증 및 프론트엔드 환경 변수
# ====================================================================


AUTH_USER_MODEL = 'users.User'

# 프론트엔드 URL을 먼저 정의하여 아래 설정들이 사용할 수 있도록 합니다.
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8080')

# 카카오 설정
KAKAO_REST_API_KEY = os.environ.get('KAKAO_REST_API_KEY', '59a25a1c255d5c3afbbcb2633d17c693')
# 🚨 수정: allauth 표준 경로를 사용하고, 끝에 슬래시(/)를 붙입니다.
KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI', 'http://localhost:8000/api/v1/auth/social/login/kakao/callback/')


# Application definition
SITE_ID = 1 # allauth 사용을 위한 필수 설정

# ----------------------------------------------------
# Django Allauth 및 소셜 로그인 설정
# ----------------------------------------------------
LOGIN_URL = FRONTEND_URL 
LOGIN_REDIRECT_URL = FRONTEND_URL
ACCOUNT_LOGOUT_REDIRECT_URL = FRONTEND_URL

# Allauth 소셜 계정 설정
SOCIALACCOUNT_PROVIDERS = {
    'kakao': {
        'APP': {
            'client_id': KAKAO_REST_API_KEY, 
            'secret': '', # 카카오는 secret key가 필요 없음
            'key': ''
        }
    }
}
INSTALLED_APPS = [
    'django.contrib.admin',
    'users',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 앱 및 DRF
    'apartment',
    'rest_framework',
    
    # allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao', 
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

# ----------------------------------------------------
# REST FRAMEWORK & REST AUTH 설정
# ----------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication', 
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # 기본 접근 권한 설정
    )
}

# ----------------------------------------------------
# MIDDLEWARE 및 CORS 설정
# ----------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # 🚨 최상단 유지
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🚨 수정: DEBUG=True일 때 모든 출처 허용 설정 (개발 편의성)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True 
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        FRONTEND_URL 
    ]


ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database (Docker/PostgreSQL 환경)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_DB_NAME'),
        'USER': os.environ.get('DJANGO_DB_USER'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD'),
        'HOST': os.environ.get('DJANGO_DB_HOST', 'db'), 
        'PORT': os.environ.get('DJANGO_DB_PORT', 5432),
    }
}
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
