#!/bin/bash
# deploy.sh — Mac 로컬: 크로스 빌드 → NAS 전송
# NAS 컨테이너 재시작은 수동으로 수행합니다.
# 사용법: ./deploy.sh
set -e

# === 환경 변수 ===
NAS_SSH="ssh -p 5422 starbee@192.168.1.57"
NAS_PATH="/volume3/V3_APPL/PJT/point-festival"
IMAGE_FILE="mc-images.tar"

echo "=== MC Point Festival — 빌드 & 전송 ==="
echo ""

# === 1/4: 크로스 빌드 (ARM → AMD64) ===
echo "=== 1/4: 이미지 빌드 (linux/amd64) ==="
docker buildx build --platform linux/amd64 -t mc-point-festival-backend:latest ./backend
docker buildx build --platform linux/amd64 -t mc-point-festival-frontend:latest ./frontend

echo ""
echo "=== 2/4: 이미지 tar 저장 ==="
docker save mc-point-festival-backend:latest mc-point-festival-frontend:latest -o $IMAGE_FILE
echo "    $(du -h $IMAGE_FILE | cut -f1) 생성됨"

echo ""
echo "=== 3/4: NAS로 전송 (SSH 파이프) ==="
cat $IMAGE_FILE | ${NAS_SSH} "cat > ${NAS_PATH}/${IMAGE_FILE}"
cat docker-compose.prod.yml | ${NAS_SSH} "cat > ${NAS_PATH}/docker-compose.yml"
cat database/init.sql | ${NAS_SSH} "cat > ${NAS_PATH}/database/init.sql"
echo "    전송 완료"

echo ""
echo "=== 4/4: 로컬 정리 ==="
rm -f $IMAGE_FILE
echo "    ${IMAGE_FILE} 삭제됨"

# 크로스 빌드로 생성된 AMD64 이미지 제거 (Mac에서 실행 불가한 이미지)
docker rmi mc-point-festival-backend:latest mc-point-festival-frontend:latest 2>/dev/null || true
echo "    크로스 빌드 이미지 제거됨"

# dangling 이미지 정리 (<none>:<none>)
docker image prune -f 2>/dev/null || true
echo "    dangling 이미지 정리됨"

echo ""
echo "=========================================="
echo "✅ 빌드 & 전송 완료!"
echo ""
echo "NAS에서 수동으로 실행하세요:"
echo "  ${NAS_SSH}"
echo "  cd ${NAS_PATH}"
echo "  sudo docker load -i ${IMAGE_FILE}"
echo "  sudo docker tag mc-point-festival-backend:latest mc-backend:latest"
echo "  sudo docker tag mc-point-festival-frontend:latest mc-frontend:latest"
echo "  sudo docker-compose down"
echo "  sudo docker-compose up -d"
echo "  sudo docker image prune -f"
echo "  rm -f ${IMAGE_FILE}"
echo "  sudo docker ps --filter 'name=mc-'"
echo "=========================================="
