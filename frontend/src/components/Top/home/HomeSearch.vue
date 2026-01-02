<template>
  <div class="search-container">
    <div class="search-wrapper">
      <button class="search-icon-btn" @click="handleSearch">
        <svg class="icon" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="6" stroke="#b0b8c1" stroke-width="2" fill="none"/>
          <line x1="16" y1="16" x2="21" y2="21" stroke="#b0b8c1" stroke-width="2" />
        </svg>
      </button>

      <input 
        v-model="searchQuery"
        type="text" 
        placeholder="지역, 지하철, 대학교 검색"
        class="search-input"
        @keyup.enter="handleSearch"
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
import { ref, defineEmits } from 'vue';

const searchQuery = ref('');
const isLocating = ref(false);

// 부모(HomePage)에게 이벤트를 보내기 위한 정의
const emit = defineEmits(['search']);

const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    alert('검색어를 입력해주세요.');
    return;
  }
  // 부모 컴포넌트로 검색어 전달
  emit('search', searchQuery.value);
};

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
      // 현재 위치의 경우 좌표를 문자열로 만들어 전달하거나 별도 로직 처리 가능
      emit('search', `${latitude.toFixed(6)},${longitude.toFixed(6)}`);
      isLocating.value = false;
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
  box-shadow: 0 1px 4px rgba(24, 144, 255, 0.15);
}

/* 검색 아이콘 버튼 스타일 */
.search-icon-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
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
}

.location-btn:hover:not(:disabled) { transform: scale(1.05); }
.location-btn:active:not(:disabled) { transform: scale(0.95); }
.location-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>