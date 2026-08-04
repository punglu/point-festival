#!/usr/bin/env bash
# MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001: native (no
# Docker) equivalent of run-w75-full-spec.sh, for environments where Docker
# is unavailable (e.g. this WSL session). Same permanent spec
# (specs-mongle/04-w75-data-wiring.spec.ts), same disposable-environment
# discipline, same trap-based cleanup -- only the Postgres provisioning
# mechanism differs (a native local cluster's own disposable database
# instead of a postgres:16.9-alpine container), and Playwright runs against
# playwright.mongle-manual.config.ts (caller-owns-lifecycle; no webServer).
#
# Process-lifecycle contract (E2E-RUNTIME-F-001's own root cause: a prior
# task-owned native launcher released Backend/Vite immediately after
# readiness, so every test failed with net::ERR_CONNECTION_REFUSED before
# reaching any product assertion). This script avoids every failure shape
# named in that finding by reusing run-w75-full-spec.sh's own already-proven
# pattern verbatim for the two service-start lines:
#   - Backend/Vite are started as `( cd dir && exec ... ) & PID=$!` at this
#     script's own top level -- never inside a `$(...)` command
#     substitution (which would capture only stdout and let the invoking
#     subshell exit immediately), and never inside a function whose own
#     return would end the subshell the background job lives in.
#   - `trap cleanup EXIT` is registered once, at top level, so it fires
#     exactly once, after this script's own last foreground command
#     (Playwright) returns -- not before.
#   - Readiness (`curl`) confirms the HTTP server answers; a *separate*
#     `kill -0 "$PID"` immediately before Playwright starts confirms the
#     process itself is still alive, so a readiness-then-crash race is
#     caught with a clear FATAL message instead of surfacing 30+ minutes
#     later as inexplicable connection-refused Playwright failures.
#   - Playwright runs in the foreground (not backgrounded, not `disown`ed);
#     this script's own process does not exit, and the EXIT trap does not
#     fire, until Playwright itself returns.
#
# Usage: tests/e2e/scripts/run-w75-full-spec-native.sh
# Exit code is Playwright's own exit code (or this script's own FATAL exit
# code if a precondition failed before Playwright ever started).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

DB_NAME="mc_w75_native_runner"
DB_USER="mc_admin"
DB_PASSWORD="${MONGLE_W75_NATIVE_DB_PASSWORD:-mc_local_dev_2026}"
DB_HOST="127.0.0.1"
DB_PORT="5432"
BACKEND_PORT="${MONGLE_W75_BACKEND_PORT:-18096}"
FRONTEND_PORT="${MONGLE_W75_FRONTEND_PORT:-5195}"
JWT_SECRET="w75-native-runner-throwaway-$(date +%s)"
PYTHON_BIN="$(pwd)/backend/.venv/bin/python"

BACKEND_PID=""
FRONTEND_PID=""

RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
RUNTIME_DIR="$(pwd)/tests/e2e/.runtime/w75-native-runner/run-$RUN_ID"
mkdir -p "$RUNTIME_DIR"
BACKEND_LOG="$RUNTIME_DIR/backend.log"
FRONTEND_LOG="$RUNTIME_DIR/frontend.log"
LAUNCHER_LOG="$RUNTIME_DIR/launcher.log"
exec > >(tee -a "$LAUNCHER_LOG") 2>&1
echo "--- runtime log directory (in-worktree, gitignored): tests/e2e/.runtime/w75-native-runner/run-$RUN_ID ---"

cleanup() {
  echo "--- tearing down W7.5 native spec runner infrastructure ---"
  if [ -n "$BACKEND_PID" ]; then
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
      echo "backend PID $BACKEND_PID alive at cleanup time, stopping it"
      kill "$BACKEND_PID" 2>/dev/null || true
    else
      echo "backend PID $BACKEND_PID already gone at cleanup time"
    fi
  fi
  if [ -n "$FRONTEND_PID" ]; then
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
      echo "frontend PID $FRONTEND_PID alive at cleanup time, stopping it"
      kill "$FRONTEND_PID" 2>/dev/null || true
    else
      echo "frontend PID $FRONTEND_PID already gone at cleanup time"
    fi
  fi
  PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS $DB_NAME;" >/dev/null 2>&1 || true
  if [ "${PLAYWRIGHT_EXIT:-1}" = "0" ]; then
    rm -rf "$RUNTIME_DIR"
  else
    echo "--- run failed: logs preserved at $RUNTIME_DIR ---"
  fi
}
trap cleanup EXIT

echo "--- creating disposable native Postgres database ($DB_NAME on existing local cluster) ---"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d postgres \
  -c "DROP DATABASE IF EXISTS $DB_NAME;" \
  -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" >/dev/null

DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
DATABASE_URL_SYNC="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

echo "--- loading baseline schema (database/init.sql) ---"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
  -v ON_ERROR_STOP=1 -f database/init.sql >/dev/null
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
  -c "SELECT 1 FROM admin_auth LIMIT 1" >/dev/null \
  || { echo "FATAL: admin_auth missing after init.sql load" >&2; exit 1; }

echo "--- running Alembic migrations to head (through 0021) ---"
(cd backend && DATABASE_URL="$DATABASE_URL" "$PYTHON_BIN" -m alembic stamp 0000_legacy_schema_baseline)
(cd backend && DATABASE_URL="$DATABASE_URL" "$PYTHON_BIN" -m alembic upgrade head)

echo "--- seeding synthetic fixture data ---"
(cd backend && PYTHONPATH=. DATABASE_URL="$DATABASE_URL" JWT_SECRET="$JWT_SECRET" "$PYTHON_BIN" scripts/phase1_seed_synthetic.py)

echo "--- generating a disposable synthetic admin password for '2t' ---"
MONGLE_W75_ADMIN_PASSWORD="$("$PYTHON_BIN" -c "import secrets; print('w75r' + secrets.token_urlsafe(18))")"
ADMIN_HASH="$("$PYTHON_BIN" -c "
import bcrypt, sys
print(bcrypt.hashpw(sys.argv[1].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
" "$MONGLE_W75_ADMIN_PASSWORD")"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c \
  "UPDATE admin_auth SET password = '$ADMIN_HASH' WHERE username = 'dad';" >/dev/null
export MONGLE_W75_ADMIN_PASSWORD

echo "--- starting backend (port $BACKEND_PORT) ---"
# Same construct as run-w75-full-spec.sh: `$!` immediately after a
# backgrounded `( ... ) &` on the same logical line gives that subshell's
# own PID, which `kill`/`kill -0` correctly target. This line is this
# script's own top-level scope, not inside any function or `$(...)`.
( cd backend && exec env DATABASE_URL="$DATABASE_URL" JWT_SECRET="$JWT_SECRET" JWT_ALGORITHM="HS256" \
  CORS_ORIGINS="http://localhost:$FRONTEND_PORT" \
  "$PYTHON_BIN" -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" \
  > "$BACKEND_LOG" 2>&1 ) & BACKEND_PID=$!
echo "backend PID: $BACKEND_PID"
BACKEND_READY=""
for _ in $(seq 1 30); do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "FATAL: backend process (PID $BACKEND_PID) exited during readiness wait -- see $BACKEND_LOG" >&2
    exit 1
  fi
  curl -s -o /dev/null "http://localhost:$BACKEND_PORT/docs" && { BACKEND_READY=1; break; }
  sleep 1
done
if [ -z "$BACKEND_READY" ]; then
  echo "FATAL: backend never became ready within 30s -- see $BACKEND_LOG" >&2
  exit 1
fi
echo "backend ready, PID $BACKEND_PID confirmed alive"

echo "--- starting frontend (port $FRONTEND_PORT) ---"
( cd frontend && exec env VITE_DEV_PROXY_TARGET="http://localhost:$BACKEND_PORT" \
  ./node_modules/.bin/vite --port "$FRONTEND_PORT" --strictPort \
  > "$FRONTEND_LOG" 2>&1 ) & FRONTEND_PID=$!
echo "frontend PID: $FRONTEND_PID"
FRONTEND_READY=""
for _ in $(seq 1 30); do
  if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo "FATAL: frontend process (PID $FRONTEND_PID) exited during readiness wait -- see $FRONTEND_LOG" >&2
    exit 1
  fi
  curl -s -o /dev/null "http://localhost:$FRONTEND_PORT/" && { FRONTEND_READY=1; break; }
  sleep 1
done
if [ -z "$FRONTEND_READY" ]; then
  echo "FATAL: frontend never became ready within 30s -- see $FRONTEND_LOG" >&2
  exit 1
fi
echo "frontend ready, PID $FRONTEND_PID confirmed alive"

# Fail-loud re-check immediately before Playwright starts, per this task's
# own Section 6: a readiness pass a few seconds ago is not proof the
# process is still alive right now.
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "FATAL: backend PID $BACKEND_PID died between readiness and Playwright start -- see $BACKEND_LOG" >&2
  exit 1
fi
if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
  echo "FATAL: frontend PID $FRONTEND_PID died between readiness and Playwright start -- see $FRONTEND_LOG" >&2
  exit 1
fi
echo "--- both services confirmed alive immediately before Playwright start (backend $BACKEND_PID, frontend $FRONTEND_PID) ---"

echo "--- running the full permanent W7.5 spec (local Playwright 1.58.2, foreground) ---"
set +e
(cd tests/e2e && MONGLE_PLAYWRIGHT_BASE_URL="http://localhost:$FRONTEND_PORT" \
  PLAYWRIGHT_BROWSERS_PATH=0 \
  ./node_modules/.bin/playwright test --config playwright.mongle-manual.config.ts \
  specs-mongle/04-w75-data-wiring.spec.ts)
PLAYWRIGHT_EXIT=$?
set -e

# Post-run evidence: were the services still alive for the whole run, or
# did one of them die mid-suite (a partial-lifecycle variant of
# E2E-RUNTIME-F-001 that readiness+pre-flight checks alone cannot catch)?
echo "--- post-Playwright service liveness check ---"
if kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "backend PID $BACKEND_PID: still alive immediately after Playwright finished"
else
  echo "backend PID $BACKEND_PID: already dead immediately after Playwright finished (see $BACKEND_LOG for its own exit reason)"
fi
if kill -0 "$FRONTEND_PID" 2>/dev/null; then
  echo "frontend PID $FRONTEND_PID: still alive immediately after Playwright finished"
else
  echo "frontend PID $FRONTEND_PID: already dead immediately after Playwright finished (see $FRONTEND_LOG for its own exit reason)"
fi

echo "--- done (exit $PLAYWRIGHT_EXIT); cleanup runs automatically on exit ---"
exit "$PLAYWRIGHT_EXIT"
