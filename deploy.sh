#!/bin/bash
# deploy.sh — OrbStack 빌드 → Synology NAS 배포
set -e

NAS_HOST="nas"
NAS_PATH="/volume1/docker/mc-point-festival"
IMAGE_FILE="mc-images.tar"

echo "=== 1/4: Building images ==="
docker-compose build

echo "=== 2/4: Saving images to tar ==="
docker save mc-point-festival-frontend:latest mc-point-festival-backend:latest -o $IMAGE_FILE

echo "=== 3/4: Transferring to NAS ==="
scp $IMAGE_FILE ${NAS_HOST}:${NAS_PATH}/
scp docker-compose.prod.yml ${NAS_HOST}:${NAS_PATH}/docker-compose.yml
scp .env ${NAS_HOST}:${NAS_PATH}/

echo "=== 4/4: Loading & restarting on NAS ==="
ssh $NAS_HOST << 'REMOTE'
cd /volume1/docker/mc-point-festival
docker load -i mc-images.tar
docker-compose down
docker-compose up -d
rm -f mc-images.tar
REMOTE

echo "=== Deploy complete ==="
rm -f $IMAGE_FILE
