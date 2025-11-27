<template>
  <div class="home-category">
    <div
      class="category-item"
      v-for="(c, idx) in categories"
      :key="idx"
      @click="goToRoute(c.route)"
    >
      <img :src="c.icon" class="category-icon" />
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
        { icon: aptImg, label: "아파트", route: "/category/apt" },
        { icon: houseImg, label: "주택", route: "/category/house" },
        { icon: oneroomImg, label: "원룸", route: "/category/oneroom" },
        { icon: officetelImg, label: "오피스텔", route: "/category/officetel" },
        { icon: storeImg, label: "상가건물", route: "/category/store" }
      ]
    };
  },

  methods: {
    goToRoute(route) {
      if (!route) return;
      this.$router.push(route).catch(() => {});
    }
  }
};
</script>

<style scoped>
.home-category {
  display: flex;
  gap: 12px;
  padding: 20px 16px;
  justify-content: space-between;
  margin-bottom: 0px; 
}
.category-item {
  text-align: center;
  cursor: pointer;
  flex: 1 1 auto;
}
.category-icon {
  width: 45px;
  height: 45px;
  object-fit: contain;
  margin-bottom: 0px;
}
.category-item p {
  margin: 0;
  font-size: 0.85rem;
  color: #444;
}
</style>