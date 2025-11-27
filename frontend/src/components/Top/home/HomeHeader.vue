<template>
  <div class="header">
    <!-- 로고 + 공지버튼 -->
    <div class="header-top">
      <div class="logo-wrapper">
        <img src="@/assets/logo.png" alt="HomePick" class="logo" />
      </div>
      <button class="notice-btn" @click="openNotice">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- 메인 텍스트 -->
    <div class="text-wrapper">
      <h1 class="main-title">이번엔<br>어디서 살아볼까요?</h1>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeHeader",
  methods: {
    openNotice() {
      console.log('공지사항 열기');
      // 공지사항 페이지로 이동 또는 모달 열기
      // this.$router.push('/notice');
    }
  }
};
</script>

<style scoped>
.header {
  padding: 18px 20px 12px 20px;
  background: #ffffff;
  border-bottom: none;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.logo-wrapper {
  flex: 1;
}

.logo {
  width: 120px;
  height: 65px;
  object-fit: contain;
}

.notice-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: #ffffff;
  border-radius: 50%;
  color: #1a1a1a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
  box-shadow: none;
}

.notice-btn:hover {
  background: #f5f5f7;
  transform: scale(1.05);
}

.notice-btn:active {
  transform: scale(0.95);
  background: #ebebf0;
}

.text-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.main-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.28;
  margin: 0;
  letter-spacing: -0.6px;
}

.sub-text {
  font-size: 0.8125rem;
  color: #8b95a0;
  font-weight: 400;
  margin: 0;
  margin-bottom: 0px;
  letter-spacing: -0.2px;
  line-height: 1.4;
}
</style>
