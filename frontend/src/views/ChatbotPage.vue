<template>
  <div class="chatbot-page">
    <!-- Header -->
    <header class="chatbot-header">
      <button class="back-btn" @click="$router.back()" aria-label="뒤로 가기">
        <svg class="back-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M15 6l-6 6 6 6" />
        </svg>
      </button>
      <div class="header-title">
        <span class="chatbot-icon" aria-hidden="true">🤖</span>
        <span class="title">홈픽 챗봇</span>
      </div>
    </header>

    <!-- Messages -->
    <main class="chat-body" ref="chatBody">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="['bubble', msg.role]"
      >
        {{ msg.text }}
      </div>
    </main>

    <!-- Input -->
    <footer class="chat-input">
      <input
        v-model="input"
        placeholder="궁금한 부동산 정보를 물어보세요"
        @keyup.enter="send"
      />
      <button @click="send">↑</button>
    </footer>
  </div>
</template>

<script setup>
import { ref } from "vue";

const input = ref("");
const chatBody = ref(null);

const messages = ref([
  { role: "bot", text: "부동산 전문 챗봇에게 궁금한걸 물어보세요!" }
]);

// ✅ 스크롤 함수 정의
const scrollToBottom = () => {
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight;
  }
};

const send = async () => {
  if (!input.value.trim()) return;

  // 1. 유저 메시지
  messages.value.push({
    role: "user",
    text: input.value
  });

  const userInput = input.value;
  input.value = "";

  scrollToBottom();

  try {
    // 2. 백엔드 호출
    const API_BASE = "http://localhost:8000";
    const res = await fetch(`${API_BASE}/api/chatbot/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userInput }),
    });

    const data = await res.json();

    // 3. 봇 메시지
    messages.value.push({
      role: "bot",
      text: data.answer
    });
  } catch (err) {
    messages.value.push({
      role: "bot",
      text: "⚠️ 서버와 연결할 수 없습니다."
    });
  }

  scrollToBottom();
};
</script>

<style scoped>
.chatbot-page {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #f9f9f9;
  position: relative;
}

/* Header */
.chatbot-header {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 80px;
  display: flex;
  align-items: center;
  padding: 18px 20px 6px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
  background: white;
  gap: 10px;
  box-sizing: border-box;
}
      
.back-btn {
  width: 30px;
  height: 30px;
  border: 1px solid #e6e6e6;
  background: #ffffff;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  cursor: pointer;
  transition: transform 0.12s ease, background 0.12s ease;
}

.back-btn:active {
  transform: scale(0.96);
}

.back-icon {
  width: 18px;
  height: 18px;
  stroke: #222;
  stroke-width: 2.2;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chatbot-icon {
  background: #3369ff;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.title {
  font-size: 16px;
}

/* Body */
.chat-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  scrollbar-gutter: stable;
  padding-right: 12px;
  scrollbar-width: none;
}

.chat-body::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

/* Bubble */
.bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 14px;
  margin-bottom: 10px;
  line-height: 1.4;
  word-break: break-word;
}

.bubble.user {
  margin-left: auto;
  background: #2f6bff;
  color: white;
}

.bubble.bot {
  margin-right: auto;
  background: white;
  border: 1px solid #ddd;
}

/* Input */
.chat-input {
  position: sticky;
  bottom: 0;
  display: flex;
  align-items: center;   
  min-height: 65px;
  padding: 0px 18px 20px;
  border-top: 1px solid #eee;
  background: white;
}

.chat-input input {
  flex: 1;
  padding: 10px 18px;
  border-radius: 20px;
  border: 1px solid #ddd;
  outline: none;
}

.chat-input button {
  margin-left: 8px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: #3369ff;
  color: white;
  font-size: 18px;
  cursor: pointer;
}
</style>
