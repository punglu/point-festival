#!/bin/bash
# deploy.sh — NAS에서 실행하는 배포 스크립트
# 사용법: ./deploy.sh
set -e

echo "=== MC Point Festival — 배포 ==="

if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다."
    echo "   cp .env.production.template .env 후 실제 값을 입력하세요."
    exit 1
fi

echo "=== 1/3: 최신 코드 ==="
git pull origin main

echo "=== 2/3: 빌드 + 실행 ==="
docker-compose up -d --build

echo "=== 3/3: 상태 확인 ==="
sleep 10
docker ps --filter "name=mc-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>/dev/null || echo "000")
if [ "$HEALTH" = "200" ]; then
    echo "✅ 배포 완료"
else
    echo "⚠️  헬스체크 실패 (HTTP $HEALTH) — docker logs mc-backend --tail 20"
fi
