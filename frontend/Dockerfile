# HomePick/frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json /app/
#COPY package-lock.json /app/

# 의존성 설치
RUN npm install

COPY . /app/
# 여기 copy nodemodule 제거 해놓음 > 이거때문인지 모르겠음 나중에 에러나면 확인 
# Vue 개발 서버 포트 노출 (docker-compose에서 8080으로 포워딩됩니다)
EXPOSE 8080

# ENTRYPOINT 또는 CMD는 docker-compose.yml의 command: npm run serve 로 대체됩니다.