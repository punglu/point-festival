#!/bin/bash
# deploy.sh — Mac에서 실행: 로컬 빌드 → NAS 전송 → 실행
set -e

NAS_PATH="/volume3/V3_APPL/PJT/point-festival"
IMAGE_FILE="mc-images.tar"
SSH_CMD="ssh -p 5422 starbee@192.168.1.57"

echo "=== 1/5: 이미지 빌드 ==="
docker-compose build --no-cache

echo "=== 2/5: 이미지 tar 저장 ==="
docker save mc-backend:latest mc-frontend:latest -o $IMAGE_FILE
echo "    $(du -h $IMAGE_FILE | cut -f1) 생성됨"

echo "=== 3/5: NAS로 전송 ==="
cat $IMAGE_FILE | ${SSH_CMD} "cat > ${NAS_PATH}/mc-images.tar"
cat docker-compose.prod.yml | ${SSH_CMD} "cat > ${NAS_PATH}/docker-compose.yml"
${SSH_CMD} "mkdir -p ${NAS_PATH}/database"
cat database/init.sql | ${SSH_CMD} "cat > ${NAS_PATH}/database/init.sql"

echo "=== 4/5: NAS에서 로드 + 실행 ==="
${SSH_CMD} << REMOTE
cd ${NAS_PATH}
sudo docker load -i mc-images.tar
sudo docker-compose down 2>/dev/null || true
sudo docker-compose up -d
rm -f mc-images.tar
echo ""
echo "컨테이너 상태:"
sudo docker ps --filter "name=mc-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
REMOTE

echo "=== 5/5: 헬스체크 ==="
sleep 10
HEALTH=$(${SSH_CMD} "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health" 2>/dev/null || echo "000")
if [ "$HEALTH" = "200" ]; then
    echo "✅ 배포 완료"
else
    echo "⚠️  헬스체크 실패 (HTTP $HEALTH)"
fi

rm -f $IMAGE_FILE
