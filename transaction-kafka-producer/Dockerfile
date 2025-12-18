FROM python:3.10-slim

# cron 설치
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# cron 파일 복사
COPY crontab /etc/cron.d/collector-cron

# 권한 설정
RUN chmod 0644 /etc/cron.d/collector-cron

# cron 등록
RUN crontab /etc/cron.d/collector-cron

# 로그 파일 생성
RUN touch /var/log/cron.log

# 컨테이너 시작 시 cron 실행
CMD ["cron", "-f"]
