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

      <!-- 추천 리스트 -->
      <HomeRecommend />

      <!-- 챗봇 -->
      <HomeChatbot />
    </div>

    <!-- 하단 탭바 (절대 위치) -->
    <div class="home-tabbar">
      <BottomTabBar />
    </div>
  </div>
</template>

<script>
import HomeHeader from "@/components/Top/home/HomeHeader.vue";
import HomeSearch from "@/components/Top/home/HomeSearch.vue";
import HomeCategory from "@/components/Top/home/HomeCategory.vue";
import HomeRecommend from "@/components/Top/home/HomeRecommend.vue";
import HomeChatbot from "@/components/Top/home/HomeChatbot.vue";
import BottomTabBar from "@/components/Bottom/BottomTabBar.vue";

export default {
  name: "HomePage",
  components: {
    HomeHeader,
    HomeSearch,
    HomeCategory,
    HomeRecommend,
    HomeChatbot,
    BottomTabBar
  }
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
</style>