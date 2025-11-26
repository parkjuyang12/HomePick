<template>
  <div class="welcome-container">
    <div class="logo-area">
      <img src="@/assets/logo.png" alt="홈픽" class="logo" />
    </div>

    <div class="content-area">
      <h1 class="main-title">
        대한민국 부동산 실거래가,<br>
        이제 <strong>홈픽</strong>으로 정확하게.
      </h1>

      <p class="sub-text">
        나만을 위한 맞춤형 부동산 정보를<br>
        지금 바로 시작하세요.
      </p>
    </div>

    <div class="action-area">
      <SocialLoginButtons 
        @login="handleSocialLogin"
        @show-more-options="showBottomSheet = true"
      />
    </div>


    <LoginMethodsBottomSheet 
      :show="showBottomSheet"
      @close="showBottomSheet = false"
      @login="handleBottomSheetLogin"
    />
  </div>
</template>

<script>
import SocialLoginButtons from '@/components/Login/SocialLoginButtons.vue';
import LoginMethodsBottomSheet from '@/components/Login/LoginMethodsBottomSheet.vue';

const KAKAO_REST_API_KEY = process.env.VUE_APP_KAKAO_REST_API_KEY || "59a25a1c255d5c3afbbcb2633d17c693"; 
const KAKAO_REDIRECT_URI = process.env.VUE_APP_KAKAO_REDIRECT_URI || "http://localhost:8000/api/v1/auth/social/login/kakao/callback/"; 
const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_REST_API_KEY}&redirect_uri=${KAKAO_REDIRECT_URI}&response_type=code&scope=profile_nickname,account_email`;

export default {
    name: 'WelcomePage',
    components: {
      SocialLoginButtons,
      LoginMethodsBottomSheet
    },
    data() {
      return {
        showBottomSheet: false
      }
    },
    mounted() {
      const token = localStorage.getItem('auth_token');
      if (token) {
        this.$router.push('/');
      }
    },
    methods: {
      handleSocialLogin(provider) {
        console.log(`${provider} 로그인 시도`);
        
        if (provider === 'kakao') {
          window.location.href = KAKAO_AUTH_URL; 
        } else if (provider === 'naver') {
          console.log('네이버 로그인 구현 필요');
        } else if (provider === 'apple') {
          console.log('애플 로그인 구현 필요');
        }
      },
      
      handleBottomSheetLogin(method) {
        console.log(`${method} 로그인 시도`);
        if (method === 'email') {
          this.$router.push('/login'); 
        } else if (method === 'phone') {
          this.$router.push('/phone-login');
        } else if (method === 'apple') {
          console.log('다른 로그인 방식 처리 필요');
        }
      }
    }
}
</script>

<style scoped>
.welcome-container {
    display: flex;
    flex-direction: column;
    height: 100%; 
    padding: 20px 24px 32px;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    text-align: center;
    box-sizing: border-box;
}


.logo-area {
    padding: 20px 0 10px;
    flex-shrink: 0;
    animation: fadeIn 0.6s ease;
}

.logo {
    width: 250px;
    height: auto;
    object-fit: contain;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px 0;
    animation: slideUp 0.8s ease;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e1e1e;
    line-height: 1.4;
    margin: 0 0 16px;
    letter-spacing: -0.5px;
}

.main-title strong {
    color: #3369FF;
    font-weight: 800;
}

.sub-text {
    font-size: 0.95rem;
    color: #757575;
    line-height: 1.6;
    margin: 0;
    font-weight: 400;
}

.action-area {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
    flex-shrink: 0; 
    animation: fadeInUp 1s ease;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 375px) {
    .welcome-container {
        padding: 16px 20px 28px;
    }
    
    .logo {
        width: 70px;
    }
    
    .main-title {
        font-size: 1.5rem;
    }
    
    .sub-text {
        font-size: 0.875rem;
    }
}

</style>