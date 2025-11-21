<template>
  <div class="welcome-container">
    <div class="content-area">
      <h1 class="main-title">
        대한민국 아파트 실거래가,<br>
        이제 <strong>홈픽</strong>으로 정확하게.
      </h1>

      <p class="sub-text">
        나만을 위한 맞춤형 부동산 정보를 지금 바로 시작하세요.
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
    methods: {
      handleSocialLogin(provider) {
        console.log(`${provider} 로그인 시도`);
        
        if (provider === 'kakao') {
          // ✅ 카카오 로그인 로직: 카카오 인증 서버로 브라우저 리다이렉트
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
    justify-content: space-between; 
    height: 100%;
    padding: 40px 25px;
    padding-bottom: 40px;
    background-color: #f5f5f7;
    text-align: center;
    box-sizing: border-box;
}

.content-area {
    flex-grow: 1; 
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    max-width: 400px;
    margin: 0 auto;
}

.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e1e1e;
    line-height: 1.4;
    margin-bottom: 10px;
}
.main-title strong {
    color: #3369FF;
}

.sub-text {
    font-size: 1rem;
    color: #757575;
}

.action-area {
    width: 100%;
    max-width: 400px; 
    margin: 0 auto;
    padding-bottom: 0;
    flex-shrink: 0;
}
</style>