#!/usr/bin/env bash
# MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001 (F2): deterministic, no-manual-
# steps runner for the full permanent W7.5 spec
# (specs-mongle/04-w75-data-wiring.spec.ts), including its `2t` (admin
# notification send) case. Independent QA previously reported `2t` as
# SKIPPED because MONGLE_W75_ADMIN_PASSWORD was not set and nothing in the
# repository generated it for them -- this script is that missing piece.
#
# What it does, in order:
#   1. Starts a dedicated, disposable postgres:16.9-alpine container (never
#      the shared mc_phase0/mc_phase1 Compose stacks, and never the
#      persistent dev stack on 15434/18001/13001 -- this is a separate,
#      throwaway environment per tests/README.md's isolation rule).
#   2. Runs `alembic upgrade head` and the repo's own synthetic seed script.
#   3. Generates a random, disposable-only admin password locally, writes
#      only its bcrypt hash into that throwaway database's `admin_auth`
#      row for username "dad" (the seed's own legacy admin), and exports
#      the plaintext to THIS SCRIPT'S OWN environment only -- it is never
#      written to a file, logged, or passed to a child process other than
#      the one Playwright run below.
#   4. Starts a throwaway backend (uvicorn) and frontend (vite) pointed at
#      that database.
#   5. Runs the full permanent spec.
#   6. Tears everything down unconditionally (trap on EXIT), whether the
#      spec passed or failed.
#
# Usage: tests/e2e/scripts/run-w75-full-spec.sh
# Exit code is Playwright's own exit code.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

DB_CONTAINER="mc_w75_spec_runner_db"
DB_PORT="${MONGLE_W75_DB_PORT:-15493}"
BACKEND_PORT="${MONGLE_W75_BACKEND_PORT:-18096}"
FRONTEND_PORT="${MONGLE_W75_FRONTEND_PORT:-5195}"
DB_NAME="mc_verify"
DB_USER="mc_verify"
DB_PASSWORD="verify-throwaway"
JWT_SECRET="w75-spec-runner-throwaway-$(date +%s)"

BACKEND_PID=""
FRONTEND_PID=""

# HARDENING-QA-F-002: this runner previously redirected its throwaway
# backend/frontend logs to /tmp/mc_w75_spec_runner_*.log -- AGENTS.md/
# rules.md prohibit agent-created project artifacts outside the worktree,
# which blocked Independent QA from running the required back-to-back
# invocations at all. Every invocation now gets its own timestamped,
# ignored, in-worktree runtime directory instead of a fixed path (so two
# concurrent or back-to-back runs never collide on the same log file).
RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
# Absolute path: the backend/frontend are started via `( cd backend/frontend
# && ... > "$LOG" )` subshells below, so a relative path here would resolve
# against the wrong directory once those subshells `cd` -- silently failing
# the redirect (and, with the process backgrounded, silently failing the
# whole backend/frontend start with no visible error at all).
RUNTIME_DIR="$(pwd)/tests/e2e/.runtime/w75-runner/run-$RUN_ID"
mkdir -p "$RUNTIME_DIR"
BACKEND_LOG="$RUNTIME_DIR/backend.log"
FRONTEND_LOG="$RUNTIME_DIR/frontend.log"
echo "--- runtime log directory (in-worktree, gitignored): tests/e2e/.runtime/w75-runner/run-$RUN_ID ---"

cleanup() {
  echo "--- tearing down W7.5 spec runner infrastructure ---"
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  docker rm -f "$DB_CONTAINER" >/dev/null 2>&1 || true
  # On a passing run the logs served their purpose and are removed so the
  # runtime directory does not accumulate across invocations; on a failing
  # run they are the diagnostic evidence and are kept, with their path
  # printed so it is never lost in scrollback.
  if [ "${PLAYWRIGHT_EXIT:-1}" = "0" ]; then
    rm -rf "$RUNTIME_DIR"
  else
    echo "--- run failed: logs preserved at $RUNTIME_DIR ---"
  fi
}
trap cleanup EXIT

echo "--- starting disposable Postgres ($DB_CONTAINER, port $DB_PORT) ---"
docker run -d --name "$DB_CONTAINER" --rm \
  -e "POSTGRES_USER=$DB_USER" -e "POSTGRES_PASSWORD=$DB_PASSWORD" -e "POSTGRES_DB=$DB_NAME" \
  -p "$DB_PORT:5432" postgres:16.9-alpine >/dev/null

echo "--- waiting for Postgres to accept a real query (not just pg_isready) ---"
# RE-QA-F-2T-RUNNER-FLAKY: `pg_isready` reported ready while the server was
# still not actually able to accept schema-creation commands on 2 of 4
# back-to-back runs (a real "relation admin_auth does not exist" / asyncpg
# ConnectionResetError followed both times) -- pg_isready only checks that
# the postmaster accepts a connection attempt, not that it can run a real
# query yet. Gate on an actual `SELECT 1` through psql, the same client the
# schema load below uses, instead.
DB_READY=""
for _ in $(seq 1 60); do
  docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" >/dev/null 2>&1 || { sleep 1; continue; }
  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" >/dev/null 2>&1 && { DB_READY=1; break; }
  sleep 1
done
if [ -z "$DB_READY" ]; then
  echo "FATAL: Postgres never became query-ready within 60s" >&2
  exit 1
fi

DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASSWORD@127.0.0.1:$DB_PORT/$DB_NAME"

echo "--- loading baseline schema + running migrations ---"
# No `|| true` here: a silently swallowed init.sql failure was the root
# cause of one of the two RE-QA-F-2T-RUNNER-FLAKY back-to-back failures
# ("relation admin_auth does not exist" surfaced much later, at the
# `UPDATE admin_auth` step below, with no hint of the real cause). `-v
# ON_ERROR_STOP=1` makes psql itself exit non-zero on the first failing
# statement, and `set -euo pipefail` (top of this script) then aborts the
# whole run immediately, loud and traceable, instead of continuing on a
# half-loaded schema.
docker exec -i "$DB_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" < database/init.sql >/dev/null
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1 FROM admin_auth LIMIT 1" >/dev/null \
  || { echo "FATAL: admin_auth missing after init.sql load" >&2; exit 1; }

# The asyncpg ConnectionResetError attempt QA observed happened on the
# *first* connection made immediately after the query-readiness gate above
# passed via a separate client (psql) -- a short retry absorbs that one
# remaining transient without masking a real, persistent migration failure
# (every attempt is logged; the loop still fails loudly if none succeed).
ALEMBIC_OK=""
for attempt in $(seq 1 5); do
  if (cd backend && DATABASE_URL="$DATABASE_URL" python3.11 -m alembic upgrade head); then
    ALEMBIC_OK=1
    break
  fi
  echo "alembic upgrade head attempt $attempt failed, retrying in 2s..." >&2
  sleep 2
done
if [ -z "$ALEMBIC_OK" ]; then
  echo "FATAL: alembic upgrade head did not succeed after 5 attempts" >&2
  exit 1
fi

echo "--- seeding synthetic fixture data ---"
(cd backend && PYTHONPATH=. DATABASE_URL="$DATABASE_URL" JWT_SECRET="$JWT_SECRET" python3.11 scripts/phase1_seed_synthetic.py)

echo "--- generating a disposable synthetic admin password for '2t' ---"
MONGLE_W75_ADMIN_PASSWORD="$(python3.11 -c "import secrets; print('w75r' + secrets.token_urlsafe(18))")"
ADMIN_HASH="$(python3.11 -c "
import bcrypt, sys
print(bcrypt.hashpw(sys.argv[1].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
" "$MONGLE_W75_ADMIN_PASSWORD")"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
  "UPDATE admin_auth SET password = '$ADMIN_HASH' WHERE username = 'dad';" >/dev/null
export MONGLE_W75_ADMIN_PASSWORD

echo "--- starting throwaway backend (port $BACKEND_PORT) ---"
# `$!` after a backgrounded `( ... ) &` subshell correctly gives that
# subshell's own PID (which `kill` also correctly tears down, along with
# the uvicorn process it exec's) -- but only when the assignment happens
# on the same logical command as the `&`, not as a separate statement
# after the subshell has already returned control to this script.
( cd backend && exec env DATABASE_URL="$DATABASE_URL" JWT_SECRET="$JWT_SECRET" JWT_ALGORITHM="HS256" \
  CORS_ORIGINS="http://localhost:$FRONTEND_PORT" \
  python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" \
  > "$BACKEND_LOG" 2>&1 ) & BACKEND_PID=$!
BACKEND_READY=""
for _ in $(seq 1 30); do
  curl -s -o /dev/null "http://localhost:$BACKEND_PORT/docs" && { BACKEND_READY=1; break; }
  sleep 1
done
if [ -z "$BACKEND_READY" ]; then
  echo "FATAL: backend never became ready within 30s -- see $BACKEND_LOG" >&2
  exit 1
fi

echo "--- starting throwaway frontend (port $FRONTEND_PORT) ---"
( cd frontend && exec env VITE_DEV_PROXY_TARGET="http://localhost:$BACKEND_PORT" \
  ./node_modules/.bin/vite --port "$FRONTEND_PORT" --strictPort \
  > "$FRONTEND_LOG" 2>&1 ) & FRONTEND_PID=$!
FRONTEND_READY=""
for _ in $(seq 1 30); do
  curl -s -o /dev/null "http://localhost:$FRONTEND_PORT/" && { FRONTEND_READY=1; break; }
  sleep 1
done
if [ -z "$FRONTEND_READY" ]; then
  echo "FATAL: frontend never became ready within 30s -- see $FRONTEND_LOG" >&2
  exit 1
fi

echo "--- running the full permanent W7.5 spec ---"
set +e
(cd tests/e2e && MONGLE_PLAYWRIGHT_BASE_URL="http://localhost:$FRONTEND_PORT" \
  ./node_modules/.bin/playwright test --config playwright.mongle-manual.config.ts \
  specs-mongle/04-w75-data-wiring.spec.ts)
PLAYWRIGHT_EXIT=$?
set -e

echo "--- done (exit $PLAYWRIGHT_EXIT); cleanup runs automatically on exit ---"
exit "$PLAYWRIGHT_EXIT"
