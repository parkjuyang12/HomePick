// frontend/src/router/index.js

// 1. Vue Router의 핵심 함수들을 임포트합니다. (필수)
import { createRouter, createWebHistory } from 'vue-router';

// 2. 라우트 정의
const routes = [
  {
    path: '/',
    name: 'Welcome',
    // ✅ 동적 임포트 방식으로 경로 지정
    component: () => import('../views/WelcomePage.vue') 
  }
  // {
  //   path: '/login',
  //   name: 'Login',
  //   // Login 페이지가 views 폴더에 있다고 가정
  //   component: () => import('../views/LoginPage.vue') 
  // },
  // {
  //   path: '/register',
  //   name: 'Register',
  //   // Register 페이지가 views 폴더에 있다고 가정
  //   component: () => import('../views/RegisterPage.vue')
  // }
];

// 3. 라우터 인스턴스 생성
const router = createRouter({
  // URL에 #이 없는 깔끔한 경로를 사용합니다.
  history: createWebHistory(), 
  routes
});

// 4. 생성된 인스턴스를 내보냅니다. (main.js에서 .use(router)에 사용)
export default router;