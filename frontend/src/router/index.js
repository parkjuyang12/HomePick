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
    path: '/auth/kakao/callback',
    name: 'KakaoCallback',
    component: () => import('../views/KakaoCallback.vue')
  },
  // {
  //   path: '/login',
  //   name: 'Login',
  //   component: () => import('../views/LoginPage.vue') 
  // },
  // {
  //   path: '/register',
  //   name: 'Register',
  //   component: () => import('../views/RegisterPage.vue')
  // }
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
  }
];

// 3. 라우터 인스턴스 생성
const router = createRouter({
  history: createWebHistory(), 
  routes
});

export default router;