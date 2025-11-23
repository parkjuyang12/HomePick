// frontend/src/router/index.js

// 1. Vue Router의 핵심 함수들을 임포트합니다. (필수)
import { createRouter, createWebHistory } from 'vue-router';

// 2. 라우트 정의
const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: () => import('../views/WelcomePage.vue') 
  },
   {
    path: "/home",
    name: "Home",
    component: () => import("@/views/HomePage.vue")
  },
  {
    path: "/policy",
    name: "Policy",
    component: () => import("@/views/PolicyPage.vue")
  },
  {
    path: "/map",
    name: "Map",
    component: () => import("@/views/MapPage.vue")
  },
  {
    path: "/favorite",
    name: "Favorite",
    component: () => import("@/views/FavoritePage.vue")
  },
  {
    path: "/more",
    name: "More",
    component: () => import("@/views/MorePage.vue")
  },

  // 기본 경로 리다이렉트
  { path: "/", redirect: "/home" }
];

// 3. 라우터 인스턴스 생성
const router = createRouter({
  // URL에 #이 없는 깔끔한 경로를 사용합니다.
  history: createWebHistory(), 
  routes
});

// 4. 생성된 인스턴스를 내보냅니다. (main.js에서 .use(router)에 사용)
export default router;