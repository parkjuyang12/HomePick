<template>
  <div class="home-page">

    <!-- 상단 헤더 -->
    <HomeHeader />

    <!-- 검색 -->
    <HomeSearch />

    <!-- 카테고리 -->
    <HomeCategory />

    <!-- 추천 리스트 -->
    <HomeRecommend />

    <HomeChatbot />

    <!-- 하단 탭바 -->
    <BottomTabBar />

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
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: 90px; /* 탭바 공간 확보 */
}
</style>
