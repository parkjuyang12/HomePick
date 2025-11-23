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
  <div class="search-wrapper">
    <svg class="icon" viewBox="0 0 24 24">
      <circle cx="11" cy="11" r="6" stroke="#8b95a1" stroke-width="2" fill="none"/>
      <line x1="16" y1="16" x2="21" y2="21" stroke="#8b95a1" stroke-width="2" />
    </svg>

    <input 
      type="text" 
      placeholder="지역, 지하철, 대학교 검색"
      class="search-input"
    />
  </div>
</template>

<style scoped>
.search-wrapper {
  display: flex;
  align-items: center;

  margin: 20px;
  padding: 12px 16px;

  background: white;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.icon {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  border: none;
  font-size: 15px;
  outline: none;
  background: transparent;
}
</style>


