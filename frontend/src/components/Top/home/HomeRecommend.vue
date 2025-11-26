<template>
  <div class="list-area">
    <h3>이런곳은 어떠세요?</h3>

    <div class="cards">
      <div class="card" v-for="item in recommends" :key="item.icon">
        <img :src="item.icon" class="rec-icon" />
      </div>
    </div>
  </div>
</template>

<script setup>
import 보험 from '@/assets/recommend/보험.png'
import 보험2 from '@/assets/recommend/보험2.png'
import 보험3 from '@/assets/recommend/보험3.png'

const recommends = [
  { icon: 보험 },
  { icon: 보험2 },
  { icon: 보험3 }
];
</script>

<style scoped>
.list-area {
  padding: 20px;
  
}

.list-area h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 15px;
  margin-top: 0;
}

.cards {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: none;
}

/* Chrome, Safari */
.cards::-webkit-scrollbar {
  display: none;
}

.card {
  min-width: 180px;
  height: 180px;
  border-radius: 12px;
  overflow: hidden;
  background: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 이미지가 카드 전체를 채움 */
.rec-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>