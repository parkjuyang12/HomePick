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
      <button class="primary-button" @click="goToLogin">
        홈픽 시작하기!! (로그인)
      </button>

      <button class="secondary-button" @click="goToRegister">
        이메일로 3초 만에 회원가입asd
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WelcomePage',
  methods: {
    goToLogin() {
      // this.$router.push('/login');
      this.$router.push('/home')
    },
    goToRegister() {
      this.$router.push('/register');
    }
  }
}
</script>

<style scoped>
.welcome-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* 내용과 버튼을 상하로 분리 */
    min-height: 100vh; /* 화면 전체 높이 사용 */
    padding: 30px 20px; /* 좌우 여백 조정 */
    background-color: #f5f5f7; /* 토스 느낌의 연한 배경 */
    text-align: center;
}

.content-area {
    flex-grow: 1; 
    display: flex;
    flex-direction: column;
    justify-content: center; /* 내용을 수직 중앙 정렬 */
    align-items: center; /* ⭐ 콘텐츠를 수평 중앙 정렬 */
    padding-top: 50px;
    max-width: 400px; /* ⭐ 최대 너비 설정 */
    margin: 0 auto; /* 중앙 정렬 */
}

.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e1e1e;
    line-height: 1.4;
    margin-bottom: 10px;
}
.main-title strong {
    color: #3369FF; /* 핵심 단어는 토스 블루로 강조 */
}

.sub-text {
    font-size: 1rem;
    color: #757575;
}

.action-area {
    width: 100%;
    max-width: 400px; /* ⭐ 버튼 영역도 중앙 정렬 및 최대 너비 제한 */
    margin: 0 auto;
    padding-bottom: 20px;
}

/* 1순위 버튼: 토스 시그니처 블루 */
.primary-button {
    width: 100%;
    height: 56px;
    background-color: #3369FF; 
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 10px;
    cursor: pointer;
    transition: background-color 0.2s; /* 사용자 경험 향상 */
}
.primary-button:active {
    background-color: #1d4cdb;
}

/* 2순위 버튼: 흰색 배경에 파란색 테두리 */
.secondary-button {
    width: 100%;
    height: 56px;
    background-color: white;
    color: #3369FF;
    border: 1px solid #d9d9d9;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}
.secondary-button:active {
    background-color: #f0f0f0;
}
</style>