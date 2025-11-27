<template>
  <div class="chat-card" @click="goChat">
    <div class="left-box">
      <div class="icon">🤖</div>
      <div class="text-area">
        <h4>챗봇에게 질문하기</h4>
        <p>부동산 정보가 궁금하다면 지금 바로 질문해보세요!</p>
      </div>
    </div>

    <div class="arrow">›</div>
  </div>
</template>

<script>
export default {
  name: "HomeChatbot",
  methods: {
    goChat() {
      this.$router.push("/chatbot");
    }
  }
};
</script>

<style scoped>
.chat-card {
  margin: 10px 16px;
  padding: 20px;
  background: #f2f2f2;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  border: 1px solid #e9e9e9;
  box-shadow: 0 3px 8px rgba(93, 63, 201, 0.05);

  cursor: pointer;
  transition: all 0.2s ease;
}

.chat-card:active {
  transform: scale(0.98);
}

.left-box {
  display: flex;
  gap: 14px;
  align-items: center;
}

.icon {
  background: #3369FF;
  color: white;
  width: 46px;
  height: 46px;
  border-radius: 14px;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 22px;
}

.text-area h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e1e1e;
}

.text-area p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #757575;
}

.arrow {
  font-size: 22px;
  color: #b4b4b4;
}
</style>
