<template>
  <div class="social-login-buttons">
    <!-- 카카오 로그인 버튼 -->
    <button class="social-button kakao" @click="$emit('login', 'kakao')">
      <svg class="button-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 3C6.5 3 2 6.6 2 11c0 2.8 1.9 5.3 4.7 6.7-.2.8-.7 2.8-.8 3.2-.1.5.2.5.4.3.2-.1 3.2-2.1 3.7-2.5.6.1 1.3.2 2 .2 5.5 0 10-3.6 10-8S17.5 3 12 3z"/>
      </svg>
      카카오로 이용하기
    </button>

    <!-- 네이버 로그인 버튼 -->
    <button class="social-button naver" @click="$emit('login', 'naver')">
      <svg class="button-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M16.273 12.845L7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727z"/>
      </svg>
      네이버로 이용하기
    </button>

    <!-- 다른 방법으로 이용하기 -->
    <button class="other-methods-button" @click="$emit('show-more-options')">
      다른 방법으로 이용하기
    </button>
  </div>
</template>

<script>
export default {
  name: 'SocialLoginButtons',
  emits: ['login', 'show-more-options']
}
</script>

<style scoped>
.social-login-buttons {
  width: 100%;
}

/* 소셜 로그인 버튼 */
.social-button {
    width: 100%;
    height: 56px;
    border: none;
    border-radius: 12px;
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s;
}

.social-button:active {
    transform: scale(0.98);
}

.button-icon {
    width: 24px;
    height: 24px;
}

/* 카카오 */
.social-button.kakao {
    background-color: #FEE500;
    color: #000000;
}

.social-button.kakao:active {
    background-color: #FDD835;
}

/* 네이버 */
.social-button.naver {
    background-color: #03C75A;
    color: white;
}

.social-button.naver:active {
    background-color: #02B350;
}

/* 다른 방법으로 이용하기 버튼 */
.other-methods-button {
    width: 100%;
    height: 48px;
    background-color: transparent;
    color: #757575;
    border: none;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: underline;
    margin-top: 8px;
}

.other-methods-button:active {
    color: #424242;
}
</style>