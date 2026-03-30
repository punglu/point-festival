# Node.js 18 Alpine (경량 이미지 - DS218+ 메모리 절약)
FROM node:18-alpine

# native 모듈(better-sqlite3) 빌드를 위한 도구
RUN apk add --no-cache python3 make g++

WORKDIR /app

# 의존성 먼저 복사 (레이어 캐싱 최적화)
COPY package.json .
RUN npm install --production

# 소스 복사
COPY server.js .

# 데이터 디렉토리 생성 (SQLite DB 저장 위치)
RUN mkdir -p /app/data

EXPOSE 3000

CMD ["node", "server.js"]
