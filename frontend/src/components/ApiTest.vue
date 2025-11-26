<template>
  <div>
    <h1>Django API 연동 테스트</h1>
    <button @click="testApi">API 호출</button>
    <p v-if="message">{{ message }}</p>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from 'axios'; // axios 설치 필요: npm install axios

export default {
  data() {
    return {
      message: '',
      error: '',
      // Django 백엔드 주소 (Docker 호스트 PC의 주소)
      API_URL: 'http://localhost:8000/api/v1/login/', 
    };
  },
  methods: {
    async testApi() {
      this.message = '호출 중...';
      this.error = '';
      try {
        // 실제 로그인 API를 호출하는 대신, GET 요청으로 서버 상태만 확인해봅니다.
        // 나중에 로그인 기능 구현 후 POST 요청으로 변경합니다.
        const response = await axios.get(this.API_URL); 
        this.message = '✅ API 호출 성공! 상태 코드: ' + response.status;
        this.error = '';
      } catch (err) {
        this.message = '';
        // 404가 뜨는 것은 API 경로가 아직 정확히 설정되지 않았을 가능성이 높습니다.
        this.error = '❌ API 호출 실패! 오류: ' + err.message;
      }
    },
  },
};
</script>
