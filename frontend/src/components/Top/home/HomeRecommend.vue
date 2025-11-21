<template>
  <div class="list-area">
    <h3>이런곳은 어떠세요?</h3>

    <div class="cards">
      <div class="card" v-for="item in recommends" :key="item.title">
        <div class="title">{{ item.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const recommends = [
  { title: "채팅 상담 가능한 지점" },
  { title: "외국어 응대 가능한 지점" },
  { title: "쉐어하우스 많은 지역" }
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
}

.cards {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}

.card {
  min-width: 180px;
  padding: 20px;
  background: #f2f2f2;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
}
</style>
