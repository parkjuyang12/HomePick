<template>
  <div class="home-category">
    <div
      class="category-item"
      v-for="(c, idx) in categories"
      :key="idx"
      @click="handleCategoryClick(c)"
    >
      <div class="icon-wrapper">
        <img :src="c.icon" class="category-icon" />
      </div>
      <p>{{ c.label }}</p>
    </div>
  </div>
</template>

<script>
import aptImg from '@/assets/category/아파트.png';
import houseImg from '@/assets/category/주택.png';
import oneroomImg from '@/assets/category/원룸.png';
import officetelImg from '@/assets/category/오피스텔.png';
import storeImg from '@/assets/category/상가건물.png';

export default {
  name: "HomeCategory",
  data() {
    return {
      categories: [
        { icon: aptImg, label: "아파트", esIndex: "realestate_current_apartment" },
        { icon: houseImg, label: "주택", esIndex: "realestate_current_house" },
        { icon: oneroomImg, label: "원룸", esIndex: "realestate_current_house" },
        { icon: officetelImg, label: "오피스텔", esIndex: "realestate_current_officetel" },
        { icon: storeImg, label: "상가건물", esIndex: "realestate_current_commercial" }
      ]
    };
  },
  methods: {
    handleCategoryClick(category) {
      // ✅ 수정: 카테고리만 전달, address는 전달하지 않음
      // MapPage에서 getCurrentLocationAndSearch가 호출되도록 함
      this.$router.push({
        path: '/map',
        query: { 
          category: category.esIndex 
          // address 제거: 현재 위치를 사용하도록 함
        }
      }).catch(() => {});
    }
  }
};
</script>

<style scoped>
.home-category {
  display: flex;
  justify-content: space-between;
  padding: 20px 16px;
  gap: 8px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  flex: 1;
  min-width: 0; /* flex 자식의 최소 크기 제한 해제 */
}

.icon-wrapper {
  width: 48px; /* 아이콘을 감싸는 컨테이너 크기 고정 */
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.category-icon {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 이미지가 넘치지 않게 고정 */
}

.category-item p {
  margin: 0;
  font-size: 0.75rem;
  color: #444;
  white-space: nowrap; /* 글자 줄바꿈 방지 */
}
</style>