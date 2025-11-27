<!-- <template>
  <div class="search-wrapper">
    <input 
      type="text" 
      placeholder="지역, 지하철, 대학교 검색"
      class="search-input"
    />
    <button class="search-btn">
      🔍
    </button>
  </div>
</template>

<script setup></script>

<style scoped>
.search-wrapper {
  display: flex;
  align-items: center;

  margin: 0 20px;
  padding: 10px 14px;

  background: #ffffff;
  border-radius: 14px;
  border: 1.5px solid #d0d7df;

  /* 소프트 그림자 (고급 앱 느낌) */
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);

  transition: border 0.2s ease;
}

.search-input {
  flex: 1;
  border: none;
  font-size: 16px;
  outline: none;
  padding-left: 4px;

  color: #333;
}

.search-input::placeholder {
  color: #B0B7C3;
}

.search-btn {
  width: 36px;
  height: 36px;
  border: none;
  outline: none;
  cursor: pointer;
  border-radius: 50%;

  background: #2DCDB1;
  color: white;
  font-size: 18px;

  display: flex;
  align-items: center;
  justify-content: center;

  transition: background 0.2s ease;
}

.search-btn:active {
  background: #1fb79d;
}
</style> -->

<template>
  <div class="search-container">
    <div class="search-wrapper">
      <svg class="icon" viewBox="0 0 24 24">
        <circle cx="11" cy="11" r="6" stroke="#b0b8c1" stroke-width="2" fill="none"/>
        <line x1="16" y1="16" x2="21" y2="21" stroke="#b0b8c1" stroke-width="2" />
      </svg>

      <input 
        type="text" 
        placeholder="지역, 지하철, 대학교 검색"
        class="search-input"
      />

      <div class="divider"></div>

      <button class="location-btn" @click="getCurrentLocation" :disabled="isLocating">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="3" fill="currentColor"/>
          <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.5" fill="none"/>
          <circle cx="12" cy="12" r="11" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.5"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isLocating = ref(false);

const getCurrentLocation = async () => {
  if (!navigator.geolocation) {
    alert('현재 브라우저에서 위치 기능을 지원하지 않습니다.');
    return;
  }

  isLocating.value = true;
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      console.log('현재 위치:', { latitude, longitude });
      // 여기서 위치를 기반으로 검색 수행
      isLocating.value = false;
      alert(`위도: ${latitude.toFixed(4)}, 경도: ${longitude.toFixed(4)}`);
    },
    (error) => {
      console.error('위치 조회 실패:', error);
      isLocating.value = false;
      alert('위치를 조회할 수 없습니다.');
    }
  );
};
</script>

<style scoped>
.search-container {
  padding: 8px 16px 8px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  background: #ffffff;
  border-radius: 12px;
  border: 1.5px solid #1890ff;
  transition: all 0.2s ease;
  gap: 8px;
}

.search-wrapper:focus-within {
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(24, 144, 255, 0.15);
}

.icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  font-size: 15px;
  outline: none;
  background: transparent;
  color: #1a1a1a;
  font-weight: 400;
  letter-spacing: -0.3px;
}

.search-input::placeholder {
  color: #b0b8c1;
}

.divider {
  width: 1px;
  height: 28px;
  background: #d0d7df;
  flex-shrink: 0;
  opacity: 0.6;
}

.location-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #ffffff;
  border-radius: 50%;
  color: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-left: 0;
}

.location-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.location-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.location-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>


