#!/usr/bin/env bash
# MONGLE-FE-E2E-HARNESS-RESTORE-001: deterministic bring-up for the isolated
# mongle stack (db+backend+frontend, ports 15434/18001/13001) that
# tests/e2e/specs-mongle/01-shell.spec.ts requires. Restored from git history
# (commit 92bd75c^) — this is a test-only isolated environment, not an
# operating/production stack. Safe to run repeatedly: `up --wait` is
# idempotent, and the synthetic seed script deletes-then-recreates its own
# fixture rows on every invocation.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

COMPOSE="docker compose -p mongle --env-file .env.phase0.example -f docker-compose.phase1.yml"

# Bring up db+backend first and seed synchronously BEFORE starting frontend.
# Playwright's webServer only polls the frontend URL, and frontend's nginx
# healthcheck is independent of DB content — if all three services started
# together, Playwright could start running tests as soon as nginx responds,
# racing ahead of the seed script (observed as non-deterministic test
# failures in an earlier run of this harness). Starting frontend last, only
# after seeding completes, makes the frontend URL a true readiness signal.

# MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001: the frontend image must
# be rebuilt from the worktree *and proven* to be. A previous run served a stale
# image and its 41 failures described source that no longer existed. `--build`
# was added then, but it is not sufficient on its own: a cached layer or an
# already-running container both defeat it silently. So the source fingerprint
# is baked into the image and re-checked after bring-up.
# Honour a value inherited from playwright.mongle.config.ts so the image is
# built with exactly the fingerprint the tests will assert against, rather than
# a second one computed a moment later.
MONGLE_FRONTEND_FINGERPRINT="${MONGLE_FRONTEND_FINGERPRINT:-$(./tests/e2e/scripts/frontend-source-fingerprint.sh)}"
export MONGLE_FRONTEND_FINGERPRINT
echo "frontend source fingerprint: $MONGLE_FRONTEND_FINGERPRINT"

$COMPOSE up -d --build --wait db backend
$COMPOSE exec -T backend python scripts/phase1_seed_synthetic.py

# `--force-recreate` on frontend so a container left over from an earlier run
# cannot keep serving its old image after a successful rebuild.
$COMPOSE up -d --build --force-recreate --wait frontend

./tests/e2e/scripts/verify-current-source-frontend.sh
