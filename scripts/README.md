# Firebase → PostgreSQL 마이그레이션 가이드

## 사전 준비

1. Firebase RTDB export JSON 확인
   - 프로젝트 루트에 `mark-point-festivals-default-rtdb-export.json` 파일이 있어야 합니다

2. Python 의존성 설치
   ```bash
   pip install psycopg2-binary bcrypt
   ```

3. PostgreSQL 실행 확인
   ```bash
   docker-compose up -d db
   ```

## 실행

```bash
# 기본 실행 (로컬 DB: mc_admin/mc_secret_2026@localhost:5432/mc_festival)
python scripts/migrate_firebase_to_pg.py

# Dry-run (INSERT 없이 로그만)
python scripts/migrate_firebase_to_pg.py --dry-run

# JSON 파일 경로 지정
python scripts/migrate_firebase_to_pg.py --json-file /path/to/export.json

# DB 접속 정보 변경
DB_HOST=localhost DB_PORT=5432 DB_NAME=mc_festival \
DB_USER=mc_admin DB_PASS=mc_secret_2026 \
python scripts/migrate_firebase_to_pg.py
```

## 검증

```bash
# Docker 컨테이너 DB에 접속하여 검증 (컨테이너명: mc-db)
docker exec -i mc-db psql -U mc_admin -d mc_festival \
  < scripts/verify_migration.sql
```

## 주의사항

- 마이그레이션은 TRUNCATE ALL로 시작하므로 기존 데이터가 삭제됩니다
- 실패 시 전체 롤백됩니다 (부분 이관 없음)
- Firebase export JSON은 절대 Git에 커밋하지 마세요 (개인정보 포함)
