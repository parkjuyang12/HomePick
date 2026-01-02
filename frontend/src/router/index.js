// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';

// 라우트 정의
const routes = [
  {
    path: '/',
    redirect: '/welcome'  // 루트 접속 시 welcome으로 리다이렉트
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('../views/WelcomePage.vue')
  },
  {
    path: '/auth/kakao/callback',
    name: 'KakaoCallback',
    component: () => import('../views/KakaoCallback.vue')
  },
  // 로그인이 필요한 페이지들
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { requiresAuth: true }  // 로그인 필요
  },
  /*
  {
    path: '/policy',
    name: 'Policy',
    component: () => import('../views/PolicyPage.vue'),
    meta: { requiresAuth: true }
  },
  */
  {
    path: '/map',
    name: 'Map',
    component: () => import('../views/MapPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/property/:id',
    name: 'PropertyDetail',
    component: () => import('../views/PropertyDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  /*
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../views/FavoritePage.vue'),
    meta: { requiresAuth: true }
  },
  */
  {
    path: '/more',
    name: 'More',
    component: () => import('../views/MorePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: "/chatbot",
    component: () => import("@/views/ChatbotPage.vue")
  }
];

// 라우터 인스턴스 생성
const router = createRouter({
  history: createWebHistory(),
  routes
});

// 네비게이션 가드 - 로그인 체크
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token');

  console.log('🔀 라우팅:', from.path, '→', to.path);
  console.log('🔑 토큰 존재:', !!token);

  // 로그인이 필요한 페이지인데 토큰이 없으면
  if (to.meta.requiresAuth && !token) {
    console.log('❌ 로그인 필요 - /welcome로 리다이렉트');
    next('/welcome');
  }
  // Welcome 페이지인데 이미 로그인되어 있으면
  else if (to.path === '/welcome' && token) {
    console.log('✅ 이미 로그인됨 - /home으로 리다이렉트');
    next('/home');
  }
  else {
    next();
  }
});

export default router;
