<template>
  <div class="callback-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <h2>로그인 중...</h2>
      <p>잠시만 기다려주세요</p>
    </div>
    
    <div v-else-if="showWelcome" class="welcome">
      <div class="welcome-icon">🎉</div>
      <h1>환영합니다!</h1>
      <p class="user-name">{{ userInfo.nickname }}님</p>
      <p class="welcome-text">홈픽에서 완벽한 아파트를 찾아보세요</p>
      <button @click="goToHome" class="start-button">
        시작하기
      </button>
      <p class="auto-redirect">{{ countdown }}초 후 자동으로 이동됩니다</p>
    </div>
    
    <div v-else-if="error" class="error">
      <div class="error-icon">😢</div>
      <h2>로그인 실패</h2>
      <p>{{ error }}</p>
      <button @click="$router.push('/')">다시 시도</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KakaoCallback',
  data() {
    return {
      loading: true,
      showWelcome: false,
      error: null,
      userInfo: null,
      isNewUser: false,
      countdown: 5,
      countdownInterval: null
    }
  },
  mounted() {
    this.handleCallback();
  },
  beforeUnmount() {
    // 컴포넌트 종료 시 타이머 정리
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
    }
  },
  methods: {
    async handleCallback() {
      try {
        // URL 파라미터 추출
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        const userId = urlParams.get('user_id');
        this.isNewUser = urlParams.get('is_new_user') === 'true';
        
        console.log('📦 받은 데이터:', { token, userId, isNewUser: this.isNewUser });
        
        if (!token) {
          throw new Error('토큰을 받지 못했습니다.');
        }
        
        // 1. 토큰 저장
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user_id', userId);
        console.log('💾 토큰 저장 완료');
        
        // 2. 사용자 정보 가져오기
        this.userInfo = await this.fetchUserInfo(token);
        localStorage.setItem('user_info', JSON.stringify(this.userInfo));
        console.log('👤 사용자 정보:', this.userInfo);
        
        // 3. 로딩 완료
        this.loading = false;
        
        // 4. 분기 처리
        if (this.isNewUser) {
          // 신규 사용자: 환영 페이지 표시
          console.log('🎉 신규 사용자 - 환영 페이지 표시');
          this.showWelcome = true;
          this.startCountdown();
        } else {
          // 기존 사용자: 0.8초 후 바로 메인으로
          console.log('✅ 기존 사용자 - 메인으로 이동');
          setTimeout(() => {
            this.goToHome();
          }, 800);
        }
        
      } catch (error) {
        console.error('❌ 콜백 처리 오류:', error);
        this.error = error.message || '로그인 처리 중 오류가 발생했습니다.';
        this.loading = false;
      }
    },
    
    async fetchUserInfo(token) {
      const response = await fetch('http://localhost:8000/api/v1/auth/social/login/me/', {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('사용자 정보를 가져올 수 없습니다.');
      }
      
      return await response.json();
    },
    
    startCountdown() {
      // 5초 카운트다운
      this.countdownInterval = setInterval(() => {
        this.countdown--;
        if (this.countdown <= 0) {
          clearInterval(this.countdownInterval);
          this.goToHome();
        }
      }, 1000);
    },
    
    goToHome() {
      // Toss 스타일 페이드 아웃 애니메이션
      const container = document.querySelector('.callback-container');
      if (container) {
        container.style.opacity = '0';
        container.style.transform = 'scale(0.95)';
      }
      
      setTimeout(() => {
        this.$router.push('/');
      }, 300);
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ============ 로딩 ============ */
.loading {
  text-align: center;
  color: white;
}

.loading h2 {
  font-size: 24px;
  margin-bottom: 10px;
  font-weight: 600;
}

.loading p {
  font-size: 14px;
  opacity: 0.9;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-left-color: white;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============ 환영 메시지 ============ */
.welcome {
  background: white;
  padding: 60px 40px;
  border-radius: 30px;
  text-align: center;
  max-width: 420px;
  width: 100%;
  animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: bounce 1s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.welcome h1 {
  font-size: 32px;
  color: #333;
  margin: 0 0 10px;
  font-weight: 700;
}

.user-name {
  font-size: 24px;
  color: #667eea;
  margin: 10px 0;
  font-weight: 700;
}

.welcome-text {
  font-size: 16px;
  color: #666;
  margin: 20px 0 40px;
  line-height: 1.6;
}

.start-button {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 15px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.start-button:active {
  transform: translateY(0);
}

.auto-redirect {
  margin-top: 20px;
  font-size: 14px;
  color: #999;
}

/* ============ 에러 ============ */
.error {
  background: white;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  border: 2px solid #ff4444;
  max-width: 400px;
  width: 100%;
  animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.error-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.error h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 700;
}

.error p {
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
  line-height: 1.6;
}

.error button {
  padding: 12px 30px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
  transition: all 0.3s ease;
}

.error button:hover {
  background: #5568d3;
}

/* ============ 모바일 대응 ============ */
@media (max-width: 480px) {
  .welcome {
    padding: 40px 30px;
  }
  
  .welcome h1 {
    font-size: 28px;
  }
  
  .user-name {
    font-size: 20px;
  }
  
  .welcome-text {
    font-size: 14px;
  }
  
  .start-button {
    padding: 16px;
    font-size: 16px;
  }
}
</style>