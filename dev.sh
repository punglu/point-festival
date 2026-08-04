#!/bin/bash
# dev.sh — WSL/네이티브 로컬 개발 서버 기동 (Docker 미사용)
#
# 전제: backend/.venv (fastapi/uvicorn/alembic 등 설치 완료), backend/.env
# (DATABASE_URL이 로컬 Postgres를 가리킴), frontend/node_modules 가 이미
# 준비되어 있어야 합니다. DB role/DB 생성은 이 스크립트의 책임이 아닙니다.
#
# 사용법: ./dev.sh [start|stop|status]  (기본값: start)
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
RUNTIME_DIR="$ROOT_DIR/.dev-runtime"
BACKEND_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONTEND_PID_FILE="$RUNTIME_DIR/frontend.pid"
BACKEND_LOG="$RUNTIME_DIR/backend.log"
FRONTEND_LOG="$RUNTIME_DIR/frontend.log"
BACKEND_PORT=8000
FRONTEND_PORT=5174

mkdir -p "$RUNTIME_DIR"

is_running() {
  local pid_file="$1"
  [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null
}

status() {
  if is_running "$BACKEND_PID_FILE"; then
    echo "backend  : RUNNING (pid $(cat "$BACKEND_PID_FILE"), http://localhost:$BACKEND_PORT)"
  else
    echo "backend  : STOPPED"
  fi
  if is_running "$FRONTEND_PID_FILE"; then
    echo "frontend : RUNNING (pid $(cat "$FRONTEND_PID_FILE"), http://localhost:$FRONTEND_PORT)"
  else
    echo "frontend : STOPPED"
  fi
}

stop() {
  for pair in "backend:$BACKEND_PID_FILE" "frontend:$FRONTEND_PID_FILE"; do
    name="${pair%%:*}"; pid_file="${pair#*:}"
    if is_running "$pid_file"; then
      kill "$(cat "$pid_file")" 2>/dev/null || true
      echo "$name 중지됨 (pid $(cat "$pid_file"))"
    fi
    rm -f "$pid_file"
  done
}

start() {
  if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "오류: $BACKEND_DIR/.env 없음. DATABASE_URL/JWT_SECRET 등을 먼저 준비하세요." >&2
    exit 1
  fi
  if [ ! -x "$BACKEND_DIR/.venv/bin/python" ]; then
    echo "오류: $BACKEND_DIR/.venv 없음. (python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)" >&2
    exit 1
  fi

  if is_running "$BACKEND_PID_FILE"; then
    echo "backend 이미 실행 중 (pid $(cat "$BACKEND_PID_FILE")), 건너뜀"
  else
    echo "backend: alembic upgrade head ..."
    (cd "$BACKEND_DIR" && set -a && source .env && set +a && .venv/bin/python -m alembic upgrade head) \
      >> "$BACKEND_LOG" 2>&1

    echo "backend: uvicorn 기동 (:$BACKEND_PORT) ..."
    (cd "$BACKEND_DIR" && set -a && source .env && set +a && \
      exec .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT") \
      >> "$BACKEND_LOG" 2>&1 &
    disown
    echo $! > "$BACKEND_PID_FILE"
  fi

  if is_running "$FRONTEND_PID_FILE"; then
    echo "frontend 이미 실행 중 (pid $(cat "$FRONTEND_PID_FILE")), 건너뜀"
  else
    echo "frontend: vite dev 기동 (:$FRONTEND_PORT) ..."
    (cd "$FRONTEND_DIR" && exec pnpm run dev) >> "$FRONTEND_LOG" 2>&1 &
    disown
    echo $! > "$FRONTEND_PID_FILE"
  fi

  echo "backend 헬스체크 대기 중..."
  for _ in $(seq 1 20); do
    if curl -sf "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
      break
    fi
    sleep 0.5
  done

  echo ""
  status
  echo ""
  echo "Frontend : http://localhost:$FRONTEND_PORT"
  echo "Backend  : http://localhost:$BACKEND_PORT"
  echo "로그      : $BACKEND_LOG / $FRONTEND_LOG"
}

case "${1:-start}" in
  start)  start ;;
  stop)   stop ;;
  status) status ;;
  *) echo "사용법: $0 [start|stop|status]" >&2; exit 1 ;;
esac
