<template>
  <div class="home-page">
    <div class="home-content">
      <HomeHeader />

      <HomeSearch @search="goToMap" />

      <HomeCategory />

      <RealTimeChart :points="36" :base="12000" />

      <HomeRecommend />
      
      <HomeChatbot />
    </div>

    <div class="home-tabbar">
      <BottomTabBar />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'; // 라우터 사용을 위해 추가
import HomeHeader from "@/components/Top/home/HomeHeader.vue";
import HomeSearch from "@/components/Top/home/HomeSearch.vue";
import HomeCategory from "@/components/Top/home/HomeCategory.vue";
import HomeRecommend from "@/components/Top/home/HomeRecommend.vue";
import BottomTabBar from "@/components/Bottom/BottomTabBar.vue";
import RealTimeChart from '@/components/Top/home/RealTimeChart.vue';
import HomeChatbot from "@/components/Top/home/HomeChatbot.vue";

const router = useRouter();

/**
 * 검색 실행 시 지도 페이지로 이동하는 함수
 * @param {string} address - 사용자가 입력한 검색어 (예: 판교역)
 */
const goToMap = (address) => {
  // router push를 통해 주소 정보를 쿼리로 담아 이동합니다.
  router.push({
    path: '/map', // 프로젝트의 실제 지도 라우트 경로 확인 필요
    query: { address: address }
  });
};
</script>

<style scoped>
.home-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  position: relative;
}

.home-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 90px;
  background: #ffffff;
}

.home-content::-webkit-scrollbar { display: none; }
.home-content { scrollbar-width: none; }

.home-tabbar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  z-index: 100;
  box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.06);
  border-top: 1px solid #f0f2f5;
}
</style>