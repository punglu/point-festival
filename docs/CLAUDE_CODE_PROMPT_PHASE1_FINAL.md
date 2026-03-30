# [Claude Code 실행 프롬프트] Phase 1: 스캐폴딩 + Auth 도메인 구현
# Gemini Final Audit PASS (2026-03-30) 반영 최종본

> **지시자:** Claude Web (Main Architect)
> **실행자:** Claude Code (Developer)
> **Task ID:** PHASE-01-EXEC-001
> **감사 상태:** Gemini Final Audit — **PASS** (40/40) + Architect Verdict — **PASS** (수정 반영 완료)
> **목표:** Docker 3-Tier 보일러플레이트 + Auth 도메인 완전 구현 + `docker-compose up` 성공

---

## 🚨 실행 전 필독사항

### 운영 환경
| 항목 | 확정 내용 |
|---|---|
| 개발 | macOS + OrbStack |
| 운영 | Synology NAS + Container Manager |
| DB | PostgreSQL **16.9** LTS (Alpine) |
| 배포 | `docker save/load` → SCP → NAS |

### 아키텍처 철칙 (위반 시 QA Fail)
1. **CSS Modules 강제**: `.module.css` 외 스타일 파일 금지 (global.css, reset.css 제외)
2. **Thin Controller**: `router.py`에 비즈니스 로직 0줄
3. **SQL Annotation**: `service.py` 핵심 함수 상단 RAW SQL 주석 필수
4. **1 Page = 1 Directory**: `src/pages/[도메인명]/` 하위 수직 응집
5. **Junction Hub**: `all_models.py`는 import만 수행
6. **Soft Delete**: SoftDeleteMixin + deleted_at IS NULL 필터링

### Gemini Audit 반영사항 (모두 아래 코드에 포함됨)
- **E-3**: `global.css`에 `[data-domain]` 기반 다크/라이트 테마 격리
- **E-4**: `src/shared/components/Button/` 공통 모듈화
- **C-4**: `players.role` 필드 + JWT role claim
- **D-3**: `docker-compose.prod.yml` 분리 (NAS 경로 반영)
- **D-4**: `nginx.conf` 리버스 프록시 `/api/` → `backend:8000`
- **B-2**: `mc_party_data` → players + daily_points 흡수, 레거시 폐기

---

## 최종 폴더 구조 (생성 대상)

```
mc-point-festival/
├── .env
├── .gitignore
├── docker-compose.yml           # 개발용
├── docker-compose.prod.yml      # 운영 (Synology NAS)
├── deploy.sh                    # 배포 스크립트
│
├── database/
│   └── init.sql                 # 11 테이블 + Seed
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── all_models.py
│       ├── domains/
│       │   ├── auth/
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schema.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   └── player/
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── schema.py
│       │       ├── service.py
│       │       └── router.py
│       └── tests/
│           └── __init__.py
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── vite-env.d.ts
        ├── styles/
        │   ├── reset.css
        │   └── global.css
        ├── shared/
        │   ├── api/
        │   │   └── httpClient.ts
        │   ├── stores/
        │   │   └── useAuthStore.ts
        │   └── components/
        │       └── Button/
        │           ├── Button.tsx
        │           ├── Button.module.css
        │           └── index.ts
        └── pages/
            └── Auth/
                ├── index.tsx
                ├── Auth.module.css
                ├── components/
                │   ├── PlayerSelector.tsx
                │   ├── PinInput.tsx
                │   └── LoginOverlay.tsx
                ├── hooks/
                │   └── useAuth.ts
                └── api/
                    └── authApi.ts
```

---

## Step 0: 프로젝트 현황 파악 + CLAUDE.md 배치

### 0-1. 현재 프로젝트 구조 파악

> **중요:** 코드 생성 전에 반드시 현재 프로젝트 디렉토리를 확인하세요.

```bash
# 현재 프로젝트 루트의 파일 목록 확인
ls -la

# 기존 레거시 파일 존재 여부 확인
echo "=== 레거시 파일 확인 ==="
for f in index.html user.html admin.html styles.css firebase.json database_rules.json 404.html package.json migrate-player-auth.js; do
  [ -f "$f" ] && echo "  존재: $f"
done
```

이 프로젝트 루트에는 Firebase 기반 레거시 파일들이 존재합니다.
**이 파일들은 절대 삭제하지 마세요.** 모든 Phase 1 작업이 완료된 후 Step 7에서 `_legacy/` 폴더로 이동합니다.

### 0-2. CLAUDE.md 배치

```bash
# CLAUDE.md를 프로젝트 루트에 배치 (별도 제공된 파일 사용)
# 이미 존재하면 스킵
[ ! -f CLAUDE.md ] && echo "⚠️ CLAUDE.md가 없습니다. PM에게 요청하세요."
```

> PM은 이 프롬프트와 함께 `CLAUDE.md` 파일을 프로젝트 루트에 배치해주세요.
> Claude Code는 매 세션 시작 시 이 파일을 읽어 아키텍처 원칙을 확인합니다.

### 0-3. 프로젝트 디렉토리 생성

```bash
# mc-point-festival/ 하위 구조가 아닌, 현재 루트에서 작업
# (프로젝트 루트 = 레거시 파일이 있는 디렉토리)
mkdir -p database
mkdir -p backend/app/{models,domains/{auth,player},tests}
mkdir -p frontend/src/{styles,shared/{api,stores,components/Button},pages/Auth/{components,hooks,api}}

# 각 도메인 __init__.py 생성
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/domains/auth/__init__.py
touch backend/app/domains/player/__init__.py
touch backend/app/tests/__init__.py
```

---

## Step 1: 루트 설정 파일

### .env

```env
# Database
POSTGRES_DB=mc_festival
POSTGRES_USER=mc_admin
POSTGRES_PASSWORD=mc_secret_2026

# Backend
DATABASE_URL=postgresql+asyncpg://mc_admin:mc_secret_2026@db:5432/mc_festival
JWT_SECRET=change-this-in-production-to-random-64-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Frontend
VITE_API_BASE_URL=/api
```

### .gitignore

```gitignore
# Python
__pycache__/
*.pyc
.venv/

# Node
node_modules/
dist/

# Docker
mc-images.tar

# Env
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

### docker-compose.yml (개발용)

```yaml
version: "3.9"

services:
  db:
    image: postgres:16.9-alpine
    container_name: mc-db
    restart: unless-stopped
    env_file: .env
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mc_admin -d mc_festival"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mc-backend
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: mc-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  pg_data:
```

### docker-compose.prod.yml (Synology NAS 운영용)

```yaml
version: "3.9"

services:
  db:
    image: postgres:16.9-alpine
    container_name: mc-db
    restart: always
    env_file: .env
    volumes:
      - /volume1/docker/mc-point-festival/pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mc_admin -d mc_festival"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: mc-backend:latest
    container_name: mc-backend
    restart: always
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

  frontend:
    image: mc-frontend:latest
    container_name: mc-frontend
    restart: always
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes: {}
```

### deploy.sh (배포 스크립트)

```bash
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
```

> `chmod +x deploy.sh` 필요

---

## Step 2: 데이터베이스

### database/init.sql

```sql
-- MC Point Festival — Initial Schema (PostgreSQL 16.9 LTS)
-- Gemini Audit PASS: 40/40 항목 통과

-- 1. Players
CREATE TABLE players (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    role            VARCHAR(10) NOT NULL DEFAULT 'player'
                    CHECK (role IN ('player', 'admin')),
    photo           TEXT,
    status_msg      VARCHAR(200),
    last_login      BIGINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 2. Player Auth
CREATE TABLE player_auth (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL UNIQUE REFERENCES players(id) ON DELETE CASCADE,
    pin_hash        VARCHAR(128) NOT NULL,
    login_attempts  INTEGER NOT NULL DEFAULT 0,
    lock_until      BIGINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 3. Missions
CREATE TABLE missions (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    text            VARCHAR(500) NOT NULL,
    point           INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','completed','failed',
                           'pending_approval','proposed','rejected')),
    sender          VARCHAR(20),
    msg             TEXT,
    proposed_by     VARCHAR(20),
    proposal_reason TEXT,
    rejection_reason TEXT,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_missions_player_date ON missions(player_id, date);

-- 4. Cheer Messages
CREATE TABLE cheer_messages (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL,
    sender          VARCHAR(20) NOT NULL CHECK (sender IN ('dad', 'mom')),
    message         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_cheer_date ON cheer_messages(date);

-- 5. Feedbacks
CREATE TABLE feedbacks (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    msg             TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 6. Feedback Replies
CREATE TABLE feedback_replies (
    id              SERIAL PRIMARY KEY,
    feedback_id     INTEGER NOT NULL REFERENCES feedbacks(id) ON DELETE CASCADE,
    sender          VARCHAR(20) NOT NULL,
    text            TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 7. Deductions
CREATE TABLE deductions (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    reason          VARCHAR(300) NOT NULL,
    amount          INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_deductions_player_date ON deductions(player_id, date);

-- 8. Daily Points
CREATE TABLE daily_points (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    earned          INTEGER NOT NULL DEFAULT 0,
    spent           INTEGER NOT NULL DEFAULT 0,
    balance         INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE(player_id, date)
);

-- 9. Notifications
CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    type            VARCHAR(30) NOT NULL,
    player_id       INTEGER REFERENCES players(id) ON DELETE SET NULL,
    title           VARCHAR(200) NOT NULL,
    body            TEXT,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 10. App Config
CREATE TABLE app_configs (
    id              SERIAL PRIMARY KEY,
    key             VARCHAR(100) NOT NULL UNIQUE,
    value           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. Login Logs
CREATE TABLE login_logs (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    success         BOOLEAN NOT NULL,
    ip_address      VARCHAR(45),
    date            DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_login_logs_player ON login_logs(player_id, created_at DESC);

-- Seed Data (개발용, PIN=1234)
-- 해시 생성: python3 -c "import bcrypt; print(bcrypt.hashpw(b'1234', bcrypt.gensalt(12)).decode())"
-- 아래 해시는 실제 '1234'와 매칭 검증 완료
INSERT INTO players (name, role) VALUES
    ('유빈', 'player'),
    ('유현', 'player'),
    ('관리자', 'admin');

INSERT INTO player_auth (player_id, pin_hash) VALUES
    (1, '$2b$12$Obp2TMVO6SxsBI4wBsPG2uPGexUoBzIgE4rDSiA0clxw.Pbd5lGlq'),
    (2, '$2b$12$Obp2TMVO6SxsBI4wBsPG2uPGexUoBzIgE4rDSiA0clxw.Pbd5lGlq'),
    (3, '$2b$12$Obp2TMVO6SxsBI4wBsPG2uPGexUoBzIgE4rDSiA0clxw.Pbd5lGlq');

INSERT INTO app_configs (key, value) VALUES
    ('photos.dad', ''), ('photos.mom', '');
```

---

## Step 3: 백엔드

### backend/Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### backend/requirements.txt

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
pydantic==2.10.3
pydantic-settings==2.7.0
python-jose[cryptography]==3.3.0
bcrypt==4.2.1
alembic==1.14.0
python-multipart==0.0.18
```

### backend/app/__init__.py

```python
```

### backend/app/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
```

### backend/app/database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### backend/app/models/__init__.py

```python
```

### backend/app/models/base.py

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
```

### backend/app/models/all_models.py

```python
"""Junction Hub: Alembic 메타데이터 수집용. import만 수행."""
from app.domains.auth.models import PlayerAuth          # noqa: F401
from app.domains.player.models import Player            # noqa: F401
# Phase 2에서 나머지 도메인 추가
```

### backend/app/domains/player/__init__.py

```python
```

### backend/app/domains/player/models.py

```python
from sqlalchemy import Column, String, Integer, BigInteger, Text
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Player(Base, SoftDeleteMixin, TimestampMixin):
    """플레이어(아이) 프로필
    Firebase 원본: mc_players/{playerId}
    Gemini C-4: role 필드 (RBAC)
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    role = Column(String(10), nullable=False, default="player")
    photo = Column(Text, nullable=True)
    status_msg = Column(String(200), nullable=True)
    last_login = Column(BigInteger, nullable=True)
```

### backend/app/domains/player/schema.py

```python
from pydantic import BaseModel


class PlayerListItem(BaseModel):
    id: int
    name: str
    role: str
    last_login: int | None = None
    is_locked: bool = False

    class Config:
        from_attributes = True
```

### backend/app/domains/player/service.py

```python
"""Player 도메인 비즈니스 로직 (Phase 1: 목록 조회만)"""
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domains.player.models import Player
from app.domains.auth.models import PlayerAuth
from app.domains.player.schema import PlayerListItem


async def get_player_list(db: AsyncSession) -> list[PlayerListItem]:
    """플레이어 목록 조회 (잠금 상태 포함)

    -- [SQL] 플레이어 목록 + 잠금 상태 조회
    -- SELECT p.id, p.name, p.role, p.last_login,
    --        pa.lock_until
    -- FROM players p
    -- LEFT JOIN player_auth pa ON pa.player_id = p.id
    -- WHERE p.deleted_at IS NULL
    -- ORDER BY p.id;
    """
    result = await db.execute(
        select(Player, PlayerAuth.lock_until)
        .outerjoin(PlayerAuth, PlayerAuth.player_id == Player.id)
        .where(Player.deleted_at.is_(None))
        .order_by(Player.id)
    )
    rows = result.all()
    now_ms = int(time.time() * 1000)

    return [
        PlayerListItem(
            id=player.id,
            name=player.name,
            role=player.role,
            last_login=player.last_login,
            is_locked=bool(lock_until and now_ms < lock_until),
        )
        for player, lock_until in rows
    ]
```

### backend/app/domains/player/router.py

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.player.schema import PlayerListItem
from app.domains.player.service import get_player_list

router = APIRouter(prefix="/api/players", tags=["Player"])


@router.get("", response_model=list[PlayerListItem])
async def list_players(db: AsyncSession = Depends(get_db)):
    """플레이어 목록 조회 (Auth 페이지 PlayerSelector용)"""
    return await get_player_list(db)
```

### backend/app/domains/auth/__init__.py

```python
```

### backend/app/domains/auth/models.py

```python
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class PlayerAuth(Base, SoftDeleteMixin, TimestampMixin):
    """플레이어 인증 정보 (PIN, 잠금 상태)
    Firebase 원본: mc_player_auth/{playerId}
    """
    __tablename__ = "player_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    pin_hash = Column(String(128), nullable=False)
    login_attempts = Column(Integer, default=0, nullable=False)
    lock_until = Column(BigInteger, nullable=True)
```

### backend/app/domains/auth/schema.py

```python
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    player_id: int
    pin: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    player_id: int
    player_name: str
    player_role: str
    message: str = "로그인 성공"
```

### backend/app/domains/auth/service.py

```python
"""Auth 도메인 비즈니스 로직
PIN 인증, 잠금 처리, JWT 발급
"""
import time
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from app.domains.auth.models import PlayerAuth
from app.domains.auth.schema import LoginRequest, LoginResponse
from app.domains.player.models import Player
from app.config import settings
from jose import jwt


MAX_ATTEMPTS = 5
LOCK_DURATION_MS = 5 * 60 * 1000  # 5분


async def authenticate_player(
    db: AsyncSession,
    req: LoginRequest
) -> LoginResponse:
    """플레이어 PIN 인증 및 JWT 발급

    -- [SQL] 플레이어 인증 정보 조회
    -- SELECT pa.id, pa.player_id, pa.pin_hash, pa.login_attempts, pa.lock_until,
    --        p.name, p.role
    -- FROM player_auth pa
    -- JOIN players p ON p.id = pa.player_id
    -- WHERE pa.player_id = :player_id
    --   AND pa.deleted_at IS NULL
    --   AND p.deleted_at IS NULL;
    """
    result = await db.execute(
        select(PlayerAuth, Player.name, Player.role)
        .join(Player, Player.id == PlayerAuth.player_id)
        .where(
            PlayerAuth.player_id == req.player_id,
            PlayerAuth.deleted_at.is_(None),
            Player.deleted_at.is_(None),
        )
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 플레이어가 아닙니다."
        )

    auth: PlayerAuth = row[0]
    player_name: str = row[1]
    player_role: str = row[2]

    # 잠금 상태 확인
    now_ms = int(time.time() * 1000)
    if auth.lock_until and now_ms < auth.lock_until:
        remaining = (auth.lock_until - now_ms) // 1000
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"🔒 {remaining}초 후에 다시 시도해주세요.",
        )

    # PIN 검증
    if not bcrypt.checkpw(req.pin.encode("utf-8"), auth.pin_hash.encode("utf-8")):
        new_attempts = auth.login_attempts + 1
        await _increment_attempts(db, auth, new_attempts, now_ms)
        await _save_login_log(db, req.player_id, success=False)

        if new_attempts >= MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="5회 실패하여 5분간 잠금되었습니다.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"잘못된 PIN입니다. ({new_attempts}/{MAX_ATTEMPTS})",
        )

    # 인증 성공: 시도 횟수 초기화 + 마지막 접속 갱신
    """
    -- [SQL] 로그인 성공 시 초기화
    -- UPDATE player_auth SET login_attempts = 0, lock_until = NULL
    --   WHERE player_id = :player_id;
    -- UPDATE players SET last_login = :now WHERE id = :player_id;
    """
    await db.execute(
        update(PlayerAuth)
        .where(PlayerAuth.player_id == req.player_id)
        .values(login_attempts=0, lock_until=None)
    )
    await db.execute(
        update(Player)
        .where(Player.id == req.player_id)
        .values(last_login=now_ms)
    )
    await _save_login_log(db, req.player_id, success=True)
    await db.commit()

    # JWT 발급 (role claim 포함)
    token = _create_jwt(req.player_id, player_name, player_role)

    return LoginResponse(
        access_token=token,
        player_id=req.player_id,
        player_name=player_name,
        player_role=player_role,
    )


async def _increment_attempts(
    db: AsyncSession, auth: PlayerAuth, new_attempts: int, now_ms: int
) -> None:
    """
    -- [SQL] 로그인 실패 시 시도 횟수 증가 (5회 도달 시 잠금)
    -- UPDATE player_auth
    -- SET login_attempts = :attempts,
    --     lock_until = CASE WHEN :attempts >= 5 THEN :lock_until ELSE lock_until END
    -- WHERE id = :auth_id;
    """
    values: dict = {"login_attempts": new_attempts}
    if new_attempts >= MAX_ATTEMPTS:
        values["lock_until"] = now_ms + LOCK_DURATION_MS
        values["login_attempts"] = 0

    await db.execute(
        update(PlayerAuth).where(PlayerAuth.id == auth.id).values(**values)
    )
    await db.commit()


async def _save_login_log(db: AsyncSession, player_id: int, success: bool) -> None:
    """
    -- [SQL] 로그인 로그 기록
    -- INSERT INTO login_logs (player_id, success, date, created_at)
    -- VALUES (:player_id, :success, CURRENT_DATE, NOW());
    """
    await db.execute(
        text(
            "INSERT INTO login_logs (player_id, success, date, created_at) "
            "VALUES (:pid, :ok, CURRENT_DATE, NOW())"
        ),
        {"pid": player_id, "ok": success},
    )


def _create_jwt(player_id: int, player_name: str, role: str) -> str:
    """JWT 토큰 생성"""
    payload = {
        "sub": str(player_id),
        "name": player_name,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

### backend/app/domains/auth/router.py

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.auth.schema import LoginRequest, LoginResponse
from app.domains.auth.service import authenticate_player

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """플레이어 PIN 로그인"""
    return await authenticate_player(db, req)


@router.post("/logout")
async def logout():
    """로그아웃 (클라이언트 측 토큰 삭제)"""
    return {"message": "로그아웃 완료"}
```

### backend/app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.auth.router import router as auth_router
from app.domains.player.router import router as player_router

app = FastAPI(
    title="MC Point Festival API",
    version="1.0.0",
    description="마인크래프트 포인트 잔치 백엔드 API",
)

# CORS (개발 환경 — 프로덕션은 nginx 프록시로 대체)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(player_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "mc-point-festival"}
```

### backend/app/tests/__init__.py

```python
```

---

## Step 4: 프론트엔드

### frontend/Dockerfile

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### frontend/nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### frontend/package.json

> **Claude Code 지시**: `npm create vite@latest . -- --template react-ts` 실행 후 아래 의존성 추가 설치:
> `npm install axios zustand react-router-dom`

### frontend/vite.config.ts

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // 개발 환경: Vite dev server → FastAPI 프록시
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### frontend/src/styles/reset.css

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}

body, h1, h2, h3, h4, p, ul, ol, li {
  margin: 0;
  padding: 0;
}

ul, ol {
  list-style: none;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}
```

### frontend/src/styles/global.css

```css
/* global.css — Gemini E-3: data-domain 테마 격리 */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&family=Black+Han+Sans&family=Inter:wght@300;500;700&display=swap');

:root {
  --bg: #f8fafc;
  --card: #ffffff;
  --accent: #10b981;
  --blue: #3b82f6;
  --text: #1e293b;
  --muted: #64748b;
  --gold: #f59e0b;
  --danger: #ef4444;
  --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  --input-bg: #f1f5f9;
}

[data-domain="home"] {
  --bg: #0f0f0f;
  --card: #1a1a1a;
  --accent: #4CAF50;
  --blue: #00B0FF;
  --text: #efefef;
  --muted: #666;
  --gold: #FFD700;
  --shadow: none;
  --input-bg: #222;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Pretendard', sans-serif;
  margin: 0;
  padding: 0;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

h1, h2, h3 { margin: 0; }

input, select, textarea {
  font-family: 'Pretendard', sans-serif;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### frontend/src/main.tsx

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/reset.css';
import './styles/global.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

### frontend/src/App.tsx

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AuthPage from './pages/Auth';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <div data-domain="home">
              <div>Home (Phase 5)</div>
            </div>
          }
        />
        <Route
          path="/user"
          element={
            <div data-domain="user">
              <AuthPage />
            </div>
          }
        />
        <Route
          path="/dashboard"
          element={
            <div data-domain="user">
              <div>User Dashboard (Phase 3)</div>
            </div>
          }
        />
        <Route
          path="/admin"
          element={
            <div data-domain="admin">
              <div>Admin Dashboard (Phase 4)</div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
```

### frontend/src/shared/api/httpClient.ts

```ts
import axios from 'axios';

export const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

httpClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('accessToken');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

httpClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      sessionStorage.removeItem('accessToken');
      localStorage.removeItem('loggedInPlayer');
      window.location.href = '/';
    }
    return Promise.reject(err);
  },
);
```

### frontend/src/shared/stores/useAuthStore.ts

```ts
import { create } from 'zustand';

interface AuthState {
  token: string | null;
  player: { id: number; name: string; role: string } | null;
  isLoggedIn: boolean;
  setLogin: (token: string, player: { id: number; name: string; role: string }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  player: null,
  isLoggedIn: false,

  setLogin: (token, player) => {
    sessionStorage.setItem('accessToken', token);
    set({ token, player, isLoggedIn: true });
  },

  logout: () => {
    sessionStorage.removeItem('accessToken');
    localStorage.removeItem('loggedInPlayer');
    localStorage.removeItem('rememberMe');
    set({ token: null, player: null, isLoggedIn: false });
  },
}));
```

### frontend/src/shared/components/Button/Button.module.css

```css
/* Gemini E-4: 공통 버튼 — styles.css 섹션 6에서 추출 */

.btn {
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Pretendard', sans-serif;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn:active {
  transform: scale(0.98);
}

.primary {
  composes: btn;
  background: var(--accent);
  color: white;
  padding: 12px 20px;
}

.primary:hover {
  background: #059669;
}

.ghost {
  composes: btn;
  background: var(--input-bg);
  color: var(--muted);
  padding: 8px 12px;
  font-size: 0.8rem;
}

.ghost:hover {
  background: #e2e8f0;
  color: var(--text);
}

.dangerSm {
  composes: btn;
  background: #fee2e2;
  color: #ef4444;
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 6px;
}

.dangerSm:hover {
  background: #fecaca;
}
```

### frontend/src/shared/components/Button/Button.tsx

```tsx
import { ButtonHTMLAttributes } from 'react';
import styles from './Button.module.css';

type ButtonVariant = 'primary' | 'ghost' | 'dangerSm';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantMap: Record<ButtonVariant, string> = {
  primary: styles.primary,
  ghost: styles.ghost,
  dangerSm: styles.dangerSm,
};

export default function Button({
  variant = 'primary',
  className,
  children,
  ...props
}: ButtonProps) {
  const cls = [variantMap[variant], className].filter(Boolean).join(' ');
  return (
    <button className={cls} {...props}>
      {children}
    </button>
  );
}
```

### frontend/src/shared/components/Button/index.ts

```ts
export { default as Button } from './Button';
```

### frontend/src/pages/Auth/Auth.module.css

```css
/* 원본: styles.css 섹션 9 (Player Selector) + 섹션 10 (Login UI) */

.playerSelector {
  background: var(--card);
  border-radius: 20px;
  padding: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 24px;
}

.playerSelectorTitle {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--muted);
  margin-bottom: 12px;
}

.playerButtons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.playerBtn {
  padding: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  transition: 0.2s;
  text-align: center;
  font-weight: 700;
  color: var(--text);
  font-family: 'Pretendard', sans-serif;
  font-size: 1rem;
}

.playerBtn:hover {
  border-color: var(--accent);
  background: #f0fdf4;
  transform: translateY(-2px);
}

.emptyState {
  text-align: center;
  padding: 20px;
  color: var(--muted);
}

.loginOverlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(8px);
}

.loginCard {
  background: white;
  border-radius: 32px;
  padding: 40px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.loginCardTitle {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 1.8rem;
  margin-bottom: 10px;
  color: var(--text);
}

.subtitle {
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 30px;
}

.pinInputContainer {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 30px 0;
}

.pinDigit {
  width: 60px;
  height: 70px;
  font-size: 2rem;
  font-weight: 800;
  text-align: center;
  border: 3px solid #e2e8f0;
  border-radius: 16px;
  outline: none;
  transition: 0.2s;
  font-family: 'Pretendard', monospace;
  -webkit-text-security: disc;
  text-security: disc;
  background: var(--input-bg);
  color: var(--text);
}

.pinDigit:focus {
  border-color: var(--accent);
  background: #f0fdf4;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.pinDigitFilled {
  composes: pinDigit;
  border-color: var(--accent);
  background: #ecfdf5;
}

.pinDigitError {
  composes: pinDigit;
  border-color: var(--danger);
  background: #fef2f2;
  animation: shake 0.4s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.autoLoginCheckbox {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
  font-size: 0.9rem;
  color: var(--muted);
}

.autoLoginCheckbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.loginError {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px;
  border-radius: 12px;
  margin: 15px 0;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid #fecaca;
}

.loginLocked {
  background: #fff7ed;
  color: #ea580c;
  padding: 15px;
  border-radius: 12px;
  margin: 15px 0;
  font-size: 0.95rem;
  font-weight: 600;
  border: 2px solid #fed7aa;
}

.loginButtons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.lastLoginInfo {
  margin-top: 15px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 0.85rem;
  color: var(--muted);
}
```

### frontend/src/pages/Auth/components/PlayerSelector.tsx

```tsx
import styles from '../Auth.module.css';

interface Player {
  id: number;
  name: string;
  isLocked: boolean;
}

interface Props {
  players: Player[];
  onSelect: (playerId: number) => void;
}

export default function PlayerSelector({ players, onSelect }: Props) {
  if (!players.length) {
    return (
      <div className={styles.playerSelector}>
        <div className={styles.emptyState}>등록된 아이가 없습니다.</div>
      </div>
    );
  }

  return (
    <div className={styles.playerSelector}>
      <h3 className={styles.playerSelectorTitle}>👦 누구의 미션을 볼까요?</h3>
      <div className={styles.playerButtons}>
        {players.map((p) => (
          <button
            key={p.id}
            className={styles.playerBtn}
            onClick={() => onSelect(p.id)}
          >
            {p.name} {p.isLocked ? '🔒' : ''}
          </button>
        ))}
      </div>
    </div>
  );
}
```

### frontend/src/pages/Auth/components/PinInput.tsx

```tsx
import { useRef, useCallback, useEffect } from 'react';
import styles from '../Auth.module.css';

interface PinInputProps {
  onComplete: (pin: string) => void;
  hasError: boolean;
  resetKey: number;
}

export default function PinInput({ onComplete, hasError, resetKey }: PinInputProps) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const values = useRef<string[]>(['', '', '', '']);

  useEffect(() => {
    values.current = ['', '', '', ''];
    inputRefs.current.forEach((ref) => {
      if (ref) ref.value = '';
    });
    inputRefs.current[0]?.focus();
  }, [resetKey]);

  const getClassName = (index: number): string => {
    if (hasError) return styles.pinDigitError;
    if (values.current[index]) return styles.pinDigitFilled;
    return styles.pinDigit;
  };

  const handleInput = useCallback(
    (index: number, rawValue: string) => {
      const cleaned = rawValue.replace(/[^0-9]/g, '');
      values.current[index] = cleaned;
      const el = inputRefs.current[index];
      if (el) el.value = cleaned;

      if (cleaned && index < 3) {
        inputRefs.current[index + 1]?.focus();
      }

      if (index === 3 && cleaned) {
        const pin = values.current.join('');
        if (pin.length === 4) {
          setTimeout(() => onComplete(pin), 300);
        }
      }
    },
    [onComplete],
  );

  const handleKeyDown = useCallback((index: number, key: string) => {
    if (key === 'Backspace' && !values.current[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  }, []);

  return (
    <div className={styles.pinInputContainer}>
      {[0, 1, 2, 3].map((i) => (
        <input
          key={i}
          ref={(el) => { inputRefs.current[i] = el; }}
          type="text"
          maxLength={1}
          inputMode="numeric"
          pattern="[0-9]"
          autoComplete="off"
          className={getClassName(i)}
          onInput={(e) => handleInput(i, (e.target as HTMLInputElement).value)}
          onKeyDown={(e) => handleKeyDown(i, e.key)}
        />
      ))}
    </div>
  );
}
```

### frontend/src/pages/Auth/components/LoginOverlay.tsx

```tsx
import { useState } from 'react';
import styles from '../Auth.module.css';
import PinInput from './PinInput';
import { Button } from '../../../shared/components/Button';

interface Props {
  playerName: string;
  lastLogin: string | null;
  onSubmit: (pin: string, rememberMe: boolean) => Promise<void>;
  onCancel: () => void;
  error: string | null;
  lockedMessage: string | null;
}

export default function LoginOverlay({
  playerName, lastLogin, onSubmit, onCancel, error, lockedMessage,
}: Props) {
  const [rememberMe, setRememberMe] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [resetKey, setResetKey] = useState(0);

  const handlePinComplete = async (pin: string) => {
    setHasError(false);
    try {
      await onSubmit(pin, rememberMe);
    } catch {
      setHasError(true);
      setTimeout(() => {
        setHasError(false);
        setResetKey((k) => k + 1);
      }, 400);
    }
  };

  return (
    <div className={styles.loginOverlay}>
      <div className={styles.loginCard}>
        <h2 className={styles.loginCardTitle}>{playerName}</h2>
        <p className={styles.subtitle}>PIN 번호를 입력하세요</p>

        <PinInput onComplete={handlePinComplete} hasError={hasError} resetKey={resetKey} />

        {error && <div className={styles.loginError}>{error}</div>}
        {lockedMessage && <div className={styles.loginLocked}>{lockedMessage}</div>}

        <div className={styles.autoLoginCheckbox}>
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          <label>로그인 상태 유지</label>
        </div>

        {lastLogin && (
          <div className={styles.lastLoginInfo}>마지막 접속: {lastLogin}</div>
        )}

        <div className={styles.loginButtons}>
          <Button variant="ghost" style={{ flex: 1 }} onClick={onCancel}>취소</Button>
          <Button variant="primary" style={{ flex: 1 }}>로그인</Button>
        </div>
      </div>
    </div>
  );
}
```

### frontend/src/pages/Auth/hooks/useAuth.ts

```ts
import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/authApi';
import { useAuthStore } from '../../../shared/stores/useAuthStore';

interface PlayerInfo {
  id: number;
  name: string;
  isLocked: boolean;
  lastLogin: string | null;
}

export function useAuth() {
  const navigate = useNavigate();
  const { setLogin } = useAuthStore();

  const [players, setPlayers] = useState<PlayerInfo[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerInfo | null>(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lockedMessage, setLockedMessage] = useState<string | null>(null);

  useEffect(() => {
    authApi.getPlayers()
      .then((list) =>
        setPlayers(
          list
            .filter((p) => p.role === 'player')
            .map((p) => ({
              id: p.id,
              name: p.name,
              isLocked: p.is_locked,
              lastLogin: p.last_login
                ? new Date(p.last_login).toLocaleString('ko-KR')
                : null,
            })),
        ),
      )
      .catch(() => setPlayers([]));
  }, []);

  const selectPlayer = useCallback(
    (playerId: number) => {
      const player = players.find((p) => p.id === playerId);
      if (!player) return;
      if (player.isLocked) {
        alert('🔒 잠금 상태입니다. 잠시 후 다시 시도해주세요.');
        return;
      }
      setSelectedPlayer(player);
      setShowOverlay(true);
      setError(null);
      setLockedMessage(null);
    },
    [players],
  );

  const submitLogin = useCallback(
    async (pin: string, rememberMe: boolean) => {
      if (!selectedPlayer) return;
      setError(null);

      try {
        const res = await authApi.login({
          player_id: selectedPlayer.id,
          pin,
          remember_me: rememberMe,
        });

        setLogin(res.access_token, {
          id: res.player_id,
          name: res.player_name,
          role: res.player_role,
        });

        if (rememberMe) {
          localStorage.setItem('loggedInPlayer', String(res.player_id));
          localStorage.setItem('rememberMe', 'true');
        }

        setShowOverlay(false);
        navigate('/dashboard');
      } catch (err: any) {
        const httpStatus = err.response?.status;
        const detail = err.response?.data?.detail || '로그인 실패';

        if (httpStatus === 423) {
          setLockedMessage(detail);
          setTimeout(() => setShowOverlay(false), 2000);
        } else {
          setError(detail);
        }
        throw err;
      }
    },
    [selectedPlayer, setLogin, navigate],
  );

  const cancelLogin = useCallback(() => {
    setShowOverlay(false);
    setSelectedPlayer(null);
    setError(null);
    setLockedMessage(null);
  }, []);

  return {
    players, selectedPlayer, showOverlay, error, lockedMessage,
    selectPlayer, submitLogin, cancelLogin,
  };
}
```

### frontend/src/pages/Auth/api/authApi.ts

```ts
import { httpClient } from '../../../shared/api/httpClient';

interface LoginPayload {
  player_id: number;
  pin: string;
  remember_me: boolean;
}

interface LoginResult {
  access_token: string;
  player_id: number;
  player_name: string;
  player_role: string;
  message: string;
}

interface PlayerListItem {
  id: number;
  name: string;
  role: string;
  last_login: number | null;
  is_locked: boolean;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<LoginResult> => {
    const { data } = await httpClient.post<LoginResult>('/api/auth/login', payload);
    return data;
  },

  logout: async (): Promise<void> => {
    await httpClient.post('/api/auth/logout');
  },

  getPlayers: async (): Promise<PlayerListItem[]> => {
    const { data } = await httpClient.get<PlayerListItem[]>('/api/players');
    return data;
  },
};
```

### frontend/src/pages/Auth/index.tsx

```tsx
import PlayerSelector from './components/PlayerSelector';
import LoginOverlay from './components/LoginOverlay';
import { useAuth } from './hooks/useAuth';

export default function AuthPage() {
  const {
    players, selectedPlayer, showOverlay,
    error, lockedMessage,
    selectPlayer, submitLogin, cancelLogin,
  } = useAuth();

  return (
    <>
      <PlayerSelector players={players} onSelect={selectPlayer} />

      {showOverlay && selectedPlayer && (
        <LoginOverlay
          playerName={selectedPlayer.name}
          lastLogin={selectedPlayer.lastLogin}
          onSubmit={submitLogin}
          onCancel={cancelLogin}
          error={error}
          lockedMessage={lockedMessage}
        />
      )}
    </>
  );
}
```

---

## Step 5: 검증

```bash
# 1. 백엔드 문법 검증
cd backend
python3 -m py_compile app/main.py && echo "✅ main.py OK"
python3 -m py_compile app/config.py && echo "✅ config.py OK"
python3 -m py_compile app/database.py && echo "✅ database.py OK"
python3 -m py_compile app/models/base.py && echo "✅ base.py OK"
python3 -m py_compile app/models/all_models.py && echo "✅ all_models.py OK"
python3 -m py_compile app/domains/auth/models.py && echo "✅ auth/models.py OK"
python3 -m py_compile app/domains/auth/schema.py && echo "✅ auth/schema.py OK"
python3 -m py_compile app/domains/auth/service.py && echo "✅ auth/service.py OK"
python3 -m py_compile app/domains/auth/router.py && echo "✅ auth/router.py OK"
python3 -m py_compile app/domains/player/models.py && echo "✅ player/models.py OK"
python3 -m py_compile app/domains/player/schema.py && echo "✅ player/schema.py OK"
python3 -m py_compile app/domains/player/service.py && echo "✅ player/service.py OK"
python3 -m py_compile app/domains/player/router.py && echo "✅ player/router.py OK"
cd ..

# 2. 프론트엔드 빌드
cd frontend
npm run build && echo "✅ FE Build OK"
cd ..

# 3. Docker 빌드
docker-compose build && echo "✅ Docker Build OK"

# 4. 기동 + 헬스 체크
docker-compose up -d
sleep 15
curl -sf http://localhost:8000/api/health && echo " ✅ API Health OK"
curl -sf http://localhost:3000 | head -1 && echo " ✅ FE Serving OK"
```

---

## Step 6: 완료 보고

```
제목: Phase 1 스캐폴딩 + Auth 도메인 구현
수행자: Claude Code
일시: [실행 시점]
Task ID: PHASE-01-EXEC-001
상태: TODO → 완료

총소요시간: XX분
생성 파일 수: 35개

검증 결과:
- [ ] BE py_compile 13/13 OK
- [ ] FE npm run build 0 errors
- [ ] docker-compose build 성공
- [ ] /api/health 200 OK
- [ ] localhost:3000 HTML 응답

다음 단계: Step 7 (레거시 정리) 후 Phase 2 설계
```

---

## Step 7: 레거시 파일 정리

> **주의:** 이 단계는 Step 5 검증이 **모두 통과한 후에만** 실행하세요.
> 검증 실패 시 레거시 파일이 참조 자료로 필요할 수 있습니다.

### 7-1. 레거시 파일을 `_legacy/` 폴더로 이동

```bash
# 프로젝트 루트에서 실행
mkdir -p _legacy

# Firebase 기반 레거시 파일 이동 (삭제가 아닌 이동!)
for f in index.html user.html admin.html styles.css firebase.json database_rules.json 404.html migrate-player-auth.js; do
  [ -f "$f" ] && mv "$f" _legacy/ && echo "  이동: $f → _legacy/"
done

# 기존 package.json (firebase-admin 의존성만 있음) 이동
[ -f "package.json" ] && [ ! -d "node_modules" ] && mv package.json _legacy/ && echo "  이동: package.json → _legacy/"

# 한글 파일명 문서도 이동
for f in 공통컴포넌트추출전략.md 마이그레이션_설계_규정; do
  [ -f "$f" ] && mv "$f" _legacy/ && echo "  이동: $f → _legacy/"
done

# node_modules 제거 (있을 경우)
[ -d "node_modules" ] && rm -rf node_modules && echo "  삭제: node_modules/"

# package-lock.json 제거 (있을 경우)
[ -f "package-lock.json" ] && rm package-lock.json && echo "  삭제: package-lock.json"
```

### 7-2. _legacy/README.md 생성

```bash
cat > _legacy/README.md << 'EOF'
# Legacy Files (Firebase 기반 원본)

이 폴더는 마이그레이션 이전의 원본 파일을 보관합니다.
**절대 수정하지 마세요.** Phase 3~5에서 CSS/HTML 참조 원본으로 사용됩니다.

| 파일 | 용도 |
|---|---|
| index.html | 홈/랭킹 페이지 (다크 테마) — Phase 5 참조 |
| user.html | 아이용 대시보드 — Phase 3 참조 |
| admin.html | 관리자 대시보드 — Phase 4 참조 |
| styles.css | 전역 CSS 1,589줄 — CSS Modules 이관 원본 |
| firebase.json | Firebase Hosting 설정 |
| database_rules.json | Firebase RTDB 보안 규칙 |
| migrate-player-auth.js | PIN 분리 마이그레이션 스크립트 |

**삭제 예정:** Phase 7 (프로덕션 배포 완료) 후 이 폴더를 삭제합니다.
EOF
echo "✅ _legacy/README.md 생성 완료"
```

### 7-3. 정리 결과 확인

```bash
echo "=== 프로젝트 루트 최종 구조 ==="
ls -la | grep -v "^total"

echo ""
echo "=== _legacy/ 내용 ==="
ls _legacy/

echo ""
echo "=== 루트에 레거시 잔여 파일 확인 ==="
for f in index.html user.html admin.html styles.css firebase.json; do
  [ -f "$f" ] && echo "  ⚠️ 잔여: $f" || echo "  ✅ 정리됨: $f"
done
```

### 7-4. CLAUDE.md 상태 갱신

Step 7 완료 후 CLAUDE.md의 Phase 1 상태를 아래와 같이 갱신하세요:

```
| **1** | **Scaffolding + Auth** | **✅ 완료** |
```

Task 목록의 P1-009도 완료로 변경:
```
| P1-009 | 레거시 파일 정리 (_legacy/ 이동) | ✅ 완료 |
```

---

## 최종 완료 보고 (Step 6 + Step 7 통합)

```
제목: Phase 1 스캐폴딩 + Auth 도메인 구현 + 레거시 정리
수행자: Claude Code
일시: [실행 시점]
Task ID: PHASE-01-EXEC-001
상태: TODO → 완료

총소요시간: XX분
생성 파일 수: 35개 + _legacy/ 정리

검증 결과:
- [ ] BE py_compile 13/13 OK
- [ ] FE npm run build 0 errors
- [ ] docker-compose build 성공
- [ ] /api/health 200 OK
- [ ] localhost:3000 HTML 응답
- [ ] 레거시 파일 _legacy/ 이동 완료
- [ ] 프로젝트 루트에 레거시 잔여 파일 0건
- [ ] CLAUDE.md 상태 갱신 완료

다음 단계: PM에게 보고 → Phase 2 설계 (Core Domains BE)
```
