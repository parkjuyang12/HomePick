# HomePick/backend/Dockerfile
FROM python:3.10-slim

# 시스템 패키지 설치: netcat(DB 대기), PostgreSQL client libraries (psycopg2 필요)
RUN apt-get update \
    && apt-get install -y netcat-openbsd postgresql-client build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint 스크립트 복사 및 실행 권한 부여
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . /app/

ENTRYPOINT ["entrypoint.sh"]

# docker-compose.yml에서 이 명령을 덮어씁니다.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
