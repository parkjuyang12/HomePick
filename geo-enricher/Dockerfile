FROM python:3.10-slim

# 컨테이너 로그를 버퍼링 없이 즉시 출력
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# 보안을 위해 비루트 사용자로 실행
RUN addgroup --system app && adduser --system --ingroup app app && chown -R app:app /app
USER app

CMD ["python", "main.py"]