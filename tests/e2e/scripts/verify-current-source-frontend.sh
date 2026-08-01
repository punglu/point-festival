#!/usr/bin/env bash
# MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001
#
# Regression guard for the defect that invalidated the previous E2E run: the
# harness started a frontend container from an image built before the source
# under test existed, and 41 failures were reported as if they described the
# current product.
#
# `--build` alone is not proof. Docker will happily reuse a cached layer, and a
# reused *container* never rebuilds at all. So this asserts the three values
# that actually have to agree:
#
#   1. the worktree source fingerprint
#   2. the fingerprint baked into the running image
#   3. the fingerprint the browser can fetch from the served app
#
# (3) is checked over HTTP against the same URL Playwright uses, which is what
# rules out "right image built, wrong container serving".
#
# It also fails if frontend/.dockerignore stops excluding node_modules, because
# the host tree is darwin-arm64 and layering it over the container's linux
# install is how the build environment silently diverges from the lockfile.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

BASE_URL="${MONGLE_PLAYWRIGHT_BASE_URL:-http://localhost:13001}"
COMPOSE="docker compose -p mc_phase1 --env-file .env.phase0.example -f docker-compose.phase1.yml"

fail() { echo "STALE_FRONTEND_GUARD: FAIL — $*" >&2; exit 1; }

# --- 1. .dockerignore still excludes the host dependency tree ----------------
[ -f frontend/.dockerignore ] || fail "frontend/.dockerignore is missing"
grep -qx 'node_modules' frontend/.dockerignore \
  || fail "frontend/.dockerignore no longer excludes node_modules"

# --- 2. the compose frontend service is built, not pulled --------------------
grep -q 'dockerfile: Dockerfile' docker-compose.phase1.yml \
  || fail "frontend service is not built from a Dockerfile"

# --- 3. worktree vs image vs browser -----------------------------------------
worktree="$(./tests/e2e/scripts/frontend-source-fingerprint.sh)"

image_ref="$($COMPOSE images -q frontend 2>/dev/null || true)"
[ -n "$image_ref" ] || fail "no frontend image is running under project mc_phase1"

image_fp="$(docker image inspect --format '{{ index .Config.Labels "org.mongle.build-fingerprint" }}' "$image_ref")"
[ -n "$image_fp" ] && [ "$image_fp" != "unset" ] \
  || fail "running frontend image carries no build fingerprint (built outside this harness?)"

served="$(curl -fsS "$BASE_URL/build-fingerprint.txt")" \
  || fail "served app exposes no build fingerprint at $BASE_URL/build-fingerprint.txt"
served_fp="$(printf '%s\n' "$served" | sed -n 's/^fingerprint=//p')"

[ "$worktree" = "$image_fp" ] \
  || fail "image was built from different source: worktree=$worktree image=$image_fp"
[ "$worktree" = "$served_fp" ] \
  || fail "served app is not the built image: worktree=$worktree served=$served_fp"

echo "STALE_FRONTEND_GUARD: PASS"
echo "  worktree fingerprint : $worktree"
echo "  image fingerprint    : $image_fp"
echo "  served fingerprint   : $served_fp"
echo "  image id             : $image_ref"
printf '%s\n' "$served" | sed -n 's/^entry=/  served entry bundle  : /p'
