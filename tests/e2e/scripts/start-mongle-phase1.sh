#!/usr/bin/env bash
# MONGLE-FE-E2E-HARNESS-RESTORE-001: deterministic bring-up for the isolated
# mc_phase1 stack (db+backend+frontend, ports 15434/18001/13001) that
# tests/e2e/specs-mongle/01-shell.spec.ts requires. Restored from git history
# (commit 92bd75c^) — this is a test-only isolated environment, not an
# operating/production stack. Safe to run repeatedly: `up --wait` is
# idempotent, and the synthetic seed script deletes-then-recreates its own
# fixture rows on every invocation.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

COMPOSE="docker compose -p mc_phase1 --env-file .env.phase0.example -f docker-compose.phase1.yml"

# Bring up db+backend first and seed synchronously BEFORE starting frontend.
# Playwright's webServer only polls the frontend URL, and frontend's nginx
# healthcheck is independent of DB content — if all three services started
# together, Playwright could start running tests as soon as nginx responds,
# racing ahead of the seed script (observed as non-deterministic test
# failures in an earlier run of this harness). Starting frontend last, only
# after seeding completes, makes the frontend URL a true readiness signal.
$COMPOSE up -d --build --wait db backend
$COMPOSE exec -T backend python scripts/phase1_seed_synthetic.py
$COMPOSE up -d --wait frontend
