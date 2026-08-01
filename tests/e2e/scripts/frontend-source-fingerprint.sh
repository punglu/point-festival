#!/usr/bin/env bash
# MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001
#
# Prints a deterministic fingerprint of the frontend source tree as it exists in
# the worktree right now.
#
# It hashes the *working tree*, not git, on purpose: the files under
# verification here are uncommitted (the storage-migration module is untracked),
# so anything derived from `git ls-files` or HEAD would happily fingerprint
# source that is not what gets built.
#
# The exclusions mirror frontend/.dockerignore. If the two drift apart the
# fingerprint stops describing the build context, so
# verify-current-source-frontend.sh checks them against each other.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."

find frontend \
  -type f \
  -not -path 'frontend/node_modules/*' \
  -not -path 'frontend/dist/*' \
  -not -path 'frontend/build/*' \
  -not -path 'frontend/coverage/*' \
  -not -path 'frontend/playwright-report/*' \
  -not -path 'frontend/test-results/*' \
  -not -path 'frontend/.git/*' \
  -not -name '*.log' \
  -not -name '.DS_Store' \
  -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
| shasum -a 256 \
| cut -d' ' -f1
