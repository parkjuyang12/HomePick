<template>
  <div class="home-page">
    <!-- 스크롤 가능한 콘텐츠 -->
    <div class="home-content">
      <!-- 상단 헤더 -->
      <HomeHeader />

      <!-- 검색 -->
      <HomeSearch />

      <!-- 카테고리 -->
      <HomeCategory />

      <!-- 실시간 차트 (카테고리 아래) -->
      <RealTimeChart :points="36" :base="12000" />

      <!-- 추천 리스트 -->
      <HomeRecommend />
      <!-- 챗봇 카드 (홈 화면에도 노출) -->
      <HomeChatbot />
    </div>

    <!-- 하단 탭바 (절대 위치) -->
    <div class="home-tabbar">
      <BottomTabBar />
    </div>
    
    <!-- 챗봇 바로가기: 헤더의 알림 아이콘 옆에 위치합니다. -->
  </div>
</template>

<script>
import HomeHeader from "@/components/Top/home/HomeHeader.vue";
import HomeSearch from "@/components/Top/home/HomeSearch.vue";
import HomeCategory from "@/components/Top/home/HomeCategory.vue";
import HomeRecommend from "@/components/Top/home/HomeRecommend.vue";
import BottomTabBar from "@/components/Bottom/BottomTabBar.vue";
import RealTimeChart from '@/components/Top/home/RealTimeChart.vue';
import HomeChatbot from "@/components/Top/home/HomeChatbot.vue";

export default {
  name: "HomePage",
  components: {
    HomeHeader,
    HomeSearch,
    HomeCategory,
    HomeRecommend,
    HomeChatbot,
    BottomTabBar,
    RealTimeChart
  }
  
};
</script>

<script setup>
</script>

<style scoped>
.home-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  position: relative;
}

/* 스크롤 가능한 콘텐츠 영역 */
.home-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 90px; /* TabBar 높이만큼 여백 */
  background: #ffffff;
}

/* 스크롤바 숨김 */
.home-content::-webkit-scrollbar {
  display: none;
}

.home-content {
  scrollbar-width: none;
}

/* 하단 탭바 - absolute로 변경 */
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

/* Floating chat button (top-right) */
.floating-chat { display:none; }
</style>