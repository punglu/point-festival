#!/usr/bin/env bash
# MONGLE-FE-E2E-HARNESS-RESTORE-001: tears down the isolated mc_phase1 stack
# (containers + its dedicated volume) after the Mongle E2E suite finishes.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

docker compose -p mc_phase1 --env-file .env.phase0.example -f docker-compose.phase1.yml down -v
