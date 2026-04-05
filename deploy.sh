#!/bin/bash
# deploy.sh — Mac에서 실행: 로컬 빌드 → NAS 전송 → 실행
# 사용법: ./deploy.sh
set -e

# === NAS 접속 정보 ===
NAS_USER="starbee"
NAS_HOST="192.168.1.57"
NAS_PORT="5422"
NAS_SSH="ssh -p ${NAS_PORT} ${NAS_USER}@${NAS_HOST}"
NAS_SCP="scp -P ${NAS_PORT}"
NAS_PATH="/volume3/V3_APPL/PJT/point-festival"
IMAGE_FILE="mc-images.tar"

echo "=== MC Point Festival — 프로덕션 배포 ==="
echo ""

# === 1/5: 로컬에서 이미지 빌드 ===
echo "=== 1/5: 이미지 빌드 (OrbStack) ==="
docker-compose build --no-cache

echo ""
echo "=== 2/5: 이미지 tar 저장 ==="
docker save mc-backend:latest mc-frontend:latest -o ${IMAGE_FILE}
echo "    $(du -h ${IMAGE_FILE} | cut -f1) 생성됨"

echo ""
echo "=== 3/5: NAS로 전송 ==="
${NAS_SCP} ${IMAGE_FILE} ${NAS_USER}@${NAS_HOST}:${NAS_PATH}/
${NAS_SCP} docker-compose.prod.yml ${NAS_USER}@${NAS_HOST}:${NAS_PATH}/docker-compose.yml
${NAS_SCP} database/init.sql ${NAS_USER}@${NAS_HOST}:${NAS_PATH}/database/init.sql

echo ""
echo "=== 4/5: NAS에서 로드 + 실행 ==="
${NAS_SSH} << REMOTE
cd ${NAS_PATH}

# 이미지 로드
docker load -i ${IMAGE_FILE}

# 컨테이너 재시작
docker-compose down
docker-compose up -d

# tar 정리
rm -f ${IMAGE_FILE}

# 상태 확인
echo ""
echo "컨테이너 상태:"
docker ps --filter "name=mc-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
REMOTE

echo ""
echo "=== 5/5: 헬스체크 ==="
sleep 10
HEALTH=$(${NAS_SSH} "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health" 2>/dev/null || echo "000")
if [ "$HEALTH" = "200" ]; then
    echo "✅ 배포 완료 — API 헬스체크 통과"
else
    echo "⚠️  헬스체크 실패 (HTTP $HEALTH)"
    echo "   확인: ${NAS_SSH} 'docker logs mc-backend --tail 20'"
fi

# 로컬 tar 정리
rm -f ${IMAGE_FILE}
