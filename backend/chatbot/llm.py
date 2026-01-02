# chatbot/llm.py
import os
import requests

GMS_API_KEY = os.getenv("GMS_API_KEY")
GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"


def call_llm(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_API_KEY}",
    }

    payload = {
        "model": "gpt-5",
        "messages": [
            {
                "role": "system",
                "content": f"""
                너는 부동산 데이터를 설명해주는 챗봇이야.
                서울과 경기권의 부동산 정보만 알려주고,
                이외 지역 질문에는
                '데이터에 존재하지 않아 답변이 불가능합니다. 현재는 서울/경기만 서비스합니다. 추후 서비스 확장예정입니다.'
                라고 답해. 또한 부동산 관련 이외 질문에는 답변하지 마.
                자연스럽고 이해하기 쉽게 답변해.    
                """
            },
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(GMS_BASE_URL, headers=headers, json=payload, timeout=50)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.ReadTimeout:
        return (
            "현재 AI 응답이 지연되고 있어요.\n"
            "잠시 후 다시 시도하거나 질문을 조금 더 구체화해 주세요."
        )

    except requests.exceptions.RequestException:
        return "AI 서버와 통신 중 문제가 발생했습니다."