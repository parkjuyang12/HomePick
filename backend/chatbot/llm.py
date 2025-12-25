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
    res = requests.post(GMS_BASE_URL, headers=headers, json=payload, timeout=30)

    if res.status_code != 200:
        raise RuntimeError(f"GMS LLM error {res.status_code}: {res.text}")

    data = res.json()
    return data["choices"][0]["message"]["content"]