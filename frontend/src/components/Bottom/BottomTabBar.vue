<template>
  <div class="tabbar">
    <TabItem
      v-for="t in tabs"
      :key="t.label"
      :label="t.label"
      :route="t.route"
      :active="current === t.route"
      @click="select(t.route)"
    />
  </div>
</template>

<script>
import TabItem from "@/components/Bottom/TabItem.vue";

export default {
  components: { TabItem },

  data() {
    return {
      current: "/home", // 기본 활성 탭
      tabs: [
        { label: "홈", route: "/home" },
        { label: "정책", route: "/policy" },
        { label: "지도", route: "/map" },
        { label: "관심", route: "/favorite" },
        { label: "더보기", route: "/more" }
      ]
    };
  },

  methods: {
    select(route) {
      this.current = route;
      this.$router.push(route);
    }
  }
};
</script>

<style scoped>
.tabbar {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;

  height: 75px;
  padding: 10px 0;

  background: white;
  border-top: 1px solid #e5e5e5;

  display: flex;
  justify-content: space-around;
  align-items: center;

  z-index: 999;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}
</style>
