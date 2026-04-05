# [Claude Code 실행 프롬프트] deploy.sh 동기화 + CLAUDE.md 정합성 업데이트

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** P7-DEPLOY-SYNC-001
> **상태:** TODO → 진행중
> **목표:** deploy.sh를 실제 운영 환경에 맞게 교체하고, CLAUDE.md의 관련 서술을 정합성 있게 갱신

---

## 배경

Phase 7 배포 과정에서 NAS 환경 제약이 발견되어, 실제 운영에서는 설계 원본과 다른 방식으로 배포가 이루어지고 있습니다.
현재 git에 커밋된 deploy.sh와 실제 동작하는 배포 방식 사이에 괴리가 있으므로 이를 동기화합니다.

### 실제 운영에서 확인된 NAS 제약 사항

| 제약 | 원인 | 대응 |
|---|---|---|
| `scp` 절대경로 불가 | Synology SFTP chroot | `cat file \| ssh "cat > path"` 파이프 방식 |
| `sudo` 필수 | docker 그룹에 starbee 미등록 | 모든 docker 명령에 `sudo` 접두 |
| ARM → AMD64 크로스 빌드 필요 | Mac(Apple Silicon) → NAS(Intel) | `docker buildx --platform linux/amd64` |
| 컨테이너 재시작은 수동 | 서비스 중단 수반, PM 판단 필요 | 스크립트에서 제외, 가이드만 출력 |

### 설계 결정: 2단계 분리

- **deploy.sh** (Mac에서 실행): 빌드 + 전송만 수행
- **NAS 컨테이너 재시작**: PM이 SSH 접속 후 수동 실행
- 스크립트 마지막에 NAS에서 실행할 명령어를 출력하여 복붙 편의 제공

---

## Task 1: deploy.sh 전체 교체

**파일:** `deploy.sh` (전체 교체)

```bash
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
```

### 주의사항
- 기존 deploy.sh 내용을 **전체 교체**합니다 (기존 내용 참고 불필요)
- 파일 권한 확인: `chmod +x deploy.sh`
- `docker-compose build` 대신 `docker buildx build --platform linux/amd64`을 사용하는 이유: Mac ARM에서 빌드한 이미지는 NAS Intel에서 실행 불가

---

## Task 2: CLAUDE.md 업데이트

CLAUDE.md에서 deploy.sh 관련 서술을 실제 동작과 일치시킵니다.

### 2-1. 섹션 16 > Phase 7 확립된 패턴 수정

**현재 내용 (찾을 텍스트):**
```
### Phase 7 확립된 패턴
- **B방식 배포**: Mac에서 `docker-compose build` → `docker save` → SSH 파이프(`cat | ssh "cat >"`) → NAS `sudo docker load` → `docker-compose up -d`
- **pgdata 보존**: `docker-compose down`은 컨테이너만 삭제. bind mount `pgdata/`는 유지됨. `init.sql`은 `pgdata/`가 빈 경우에만 실행
- **init.sql 마운트 필수**: `docker-compose.prod.yml`에 `./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql` 없으면 최초 기동 시 빈 DB
- **NAS SSH 파이프**: Synology SFTP chroot로 `scp` 절대경로 불가 → `cat file | ssh "cat > path"` 방식
```

**교체할 내용:**
```
### Phase 7 확립된 패턴
- **2단계 배포**: deploy.sh(Mac)는 빌드+전송만 수행. NAS 컨테이너 재시작은 PM이 SSH 접속 후 수동 실행
- **크로스 빌드**: Mac ARM → NAS AMD64이므로 `docker buildx build --platform linux/amd64` 필수. `docker-compose build` 사용 금지
- **SSH 파이프 전송**: Synology SFTP chroot로 `scp` 절대경로 불가 → `cat file | ssh "cat > path"` 방식
- **NAS sudo 필수**: docker 그룹 미등록 → 모든 docker 명령에 `sudo` 접두
- **docker tag 필수**: 로컬 빌드명 `mc-point-festival-backend` → prod 참조명 `mc-backend`로 태깅
- **pgdata 보존**: `docker-compose down`은 컨테이너만 삭제. bind mount `pgdata/`는 유지됨. `init.sql`은 `pgdata/`가 빈 경우에만 실행
- **init.sql 마운트 필수**: `docker-compose.prod.yml`에 `./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql` 없으면 최초 기동 시 빈 DB
```

### 2-2. 섹션 16 > P7-INFRA-005 설명 수정

**현재 내용 (찾을 텍스트):**
```
| P7-INFRA-005 | `deploy.sh`: Mac 로컬 빌드 → SSH 파이프 전송 → NAS sudo docker 실행 | ✅ 완료 |
```

**교체할 내용:**
```
| P7-INFRA-005 | `deploy.sh`: Mac 크로스 빌드(`buildx amd64`) → SSH 파이프 전송. NAS 컨테이너 재시작은 수동 | ✅ 완료 |
```

### 2-3. 섹션 3 > 인프라 항목에 배포 패턴 보강

**현재 내용 (찾을 텍스트):**
```
### 인프라
- **Docker 3-Tier**: Frontend(Nginx) / Backend(FastAPI) / DB(PostgreSQL) 분리
- **개발**: `docker-compose.yml` (볼륨 마운트, 핫 리로드)
- **운영**: `docker-compose.prod.yml` (이미지 기반, NAS 경로)
```

**교체할 내용:**
```
### 인프라
- **Docker 3-Tier**: Frontend(Nginx) / Backend(FastAPI) / DB(PostgreSQL) 분리
- **개발**: `docker-compose.yml` (볼륨 마운트, 핫 리로드)
- **운영**: `docker-compose.prod.yml` (이미지 기반, NAS 경로)
- **배포**: `deploy.sh`는 빌드+전송만 (크로스 빌드 `buildx amd64` + SSH 파이프). NAS 컨테이너 재시작은 PM 수동
```

---

## 검증

```bash
# 1. deploy.sh 문법 확인
bash -n deploy.sh

# 2. 실행 권한 확인
ls -la deploy.sh | grep "x"

# 3. CLAUDE.md 변경 확인 — 아래 키워드가 모두 존재하는지 grep
grep -c "2단계 배포" CLAUDE.md        # 1 이상
grep -c "크로스 빌드" CLAUDE.md        # 1 이상
grep -c "buildx amd64" CLAUDE.md      # 2 이상 (섹션 3 + 섹션 16)
grep -c "PM 수동" CLAUDE.md           # 2 이상 (섹션 3 + 섹션 16)
```

---

## 완료 보고 형식

```
Task ID: P7-DEPLOY-SYNC-001
상태: 진행중 → 완료
총소요시간: _분
수정 파일:
  - deploy.sh (전체 교체 — 2단계 분리: 빌드+전송만)
  - CLAUDE.md (섹션 3, 섹션 16 deploy.sh 관련 서술 동기화)
검증:
  - bash -n deploy.sh — 통과
  - chmod +x deploy.sh — 확인
  - CLAUDE.md grep 키워드 — 전체 통과
```
