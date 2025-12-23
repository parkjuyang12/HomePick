# chatbot/responder.py
from .llm import call_llm  # 나중에 교체 가능

class ChatbotResponder:
    def __init__(self):
        self.mode = "LLM_ONLY"  # 나중에 RAG로 변경

    def respond(self, user_message: str) -> str:
        if self.mode == "LLM_ONLY":
            return self._llm_only_response(user_message)

        # 🔮 미래 확장
        # elif self.mode == "RAG":
        #     return self._rag_response(user_message)

        raise ValueError("Invalid chatbot mode")

    def _llm_only_response(self, message: str) -> str:
        return call_llm(message)