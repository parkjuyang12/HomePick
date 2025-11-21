<template>
  <!-- 바텀시트 오버레이 -->
  <div 
    v-if="show" 
    class="bottom-sheet-overlay"
    @click="$emit('close')"
  >
    <!-- 바텀시트 -->
    <div 
      class="bottom-sheet" 
      @click.stop
      :class="{ 'show': show }"
    >
      <div class="bottom-sheet-header">
        <div class="bottom-sheet-handle"></div>
        <h3>소셜 로그인으로 빠르게 시작하기</h3>
        <p class="bottom-sheet-subtitle">로그인 방법을 선택해주세요</p>
      </div>

      <div class="bottom-sheet-content">
        <!-- 애플 로그인 -->
        <button class="bottom-sheet-button apple" @click="handleLogin('apple')">
          <svg class="button-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
          </svg>
          <span>Apple로 로그인</span>
        </button>

        <!-- 이메일 로그인 -->
        <button class="bottom-sheet-button email" @click="handleLogin('email')">
          <svg class="button-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
          </svg>
          <span>이메일로 로그인</span>
        </button>

        <!-- 휴대폰 번호 로그인 -->
        <button class="bottom-sheet-button phone" @click="handleLogin('phone')">
          <svg class="button-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/>
          </svg>
          <span>휴대폰 번호로 이용하기</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginMethodsBottomSheet',
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  emits: ['close', 'login'],
  methods: {
    handleLogin(method) {
      this.$emit('login', method);
      this.$emit('close');
    }
  }
}
</script>

<style scoped>
.bottom-sheet-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    animation: fadeIn 0.3s ease;
    border-radius: 48px; /* 화면과 같은 border-radius */
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.bottom-sheet {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    border-radius: 24px 24px 48px 48px; 
    padding: 24px;
    padding-bottom: 40px;
    z-index: 1001;
    transform: translateY(100%);
    transition: transform 0.3s ease;
}

.bottom-sheet.show {
    transform: translateY(0);
}

.bottom-sheet-header {
    text-align: center;
    margin-bottom: 24px;
}

.bottom-sheet-handle {
    width: 40px;
    height: 4px;
    background-color: #e0e0e0;
    border-radius: 2px;
    margin: 0 auto 16px;
}

.bottom-sheet-header h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e1e1e;
    margin: 0 0 8px 0;
}

.bottom-sheet-subtitle {
    font-size: 0.9rem;
    color: #757575;
    margin: 0;
}

.bottom-sheet-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.bottom-sheet-button {
    width: 100%;
    height: 56px;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    background-color: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    transition: all 0.2s;
}

.bottom-sheet-button:active {
    transform: scale(0.98);
    background-color: #f5f5f5;
}

.bottom-sheet-button .button-icon {
    width: 24px;
    height: 24px;
}

/* 애플 */
.bottom-sheet-button.apple {
    background-color: #000000;
    border-color: #000000;
    color: white;
}

.bottom-sheet-button.apple:active {
    background-color: #1a1a1a;
}

/* 이메일 */
.bottom-sheet-button.email {
    color: #424242;
}

.bottom-sheet-button.email .button-icon {
    color: #757575;
}

/* 휴대폰 */
.bottom-sheet-button.phone {
    color: #424242;
}

.bottom-sheet-button.phone .button-icon {
    color: #757575;
}
</style>