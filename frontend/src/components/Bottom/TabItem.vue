<template>
  <div class="tab-item" @click="go">
    <img :src="icon" :class="{ active: isActive }" class="tab-icon" />
  </div>
</template>

<script>
import homeIcon from '@/assets/tabitem/홈.png';
import mapIcon from '@/assets/tabitem/지도.png';
import favoriteIcon from '@/assets/tabitem/관심.png';
import policyIcon from '@/assets/tabitem/정책.png';
import moreIcon from '@/assets/tabitem/더보기.png';

export default {
  props: {
    label: { type: String, required: true },
    route: { type: String, required: true }
  },

  computed: {
    icon() {
      const map = {
        홈: homeIcon,
        지도: mapIcon,
        관심: favoriteIcon,
        정책: policyIcon,
        더보기: moreIcon
      };
      return map[this.label] || homeIcon;
    },

    // 🔥 현재 라우트 기반 active 자동 계산
    isActive() {
      return this.$route.path === this.route;
    }
  },

  methods: {
    go() {
      this.$router.push(this.route);
    }
  }
};
</script>

<style scoped>
.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  cursor: pointer;
}

.tab-icon {
  width: 28px;
  height: 28px;
  opacity: 0.6;
  transition: all 0.2s ease;
}

/* active 상태 효과 */
.tab-icon.active {
  opacity: 1;
  transform: scale(1.2);
}
</style>
