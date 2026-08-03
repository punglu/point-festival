# Focused Independent QA — MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001

```text
Task: MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001
Target: MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001
Observed: 2026-08-03, dev-newmarkp, f8003c50f2db4df5f3af1276f921812038cfb3bc
Verdict: FAIL
```

## Baseline and integrity

Start worktree was `/Users/mac/mac_Project/mongle_ui`, with pre-existing dirty
implementation/Agent-System files and staged deletion of
`tests/e2e/test-results/.last-run.json`; stash was empty. Persistent
`mongle-db-1`/backend/frontend were observed but never used. SHA-256 manifest
was captured for migration 0021, Wagle model/service/tests, admin auth
service/schema/tests, runner, README, Playwright config, `.gitignore`, target
handoff/evidence, Coverage Map, active and relay records. QA made no product,
test, migration, or seed change. The sole QA result artifact is this report;
relay declaration was made before it.

## Migration 0021 — FAIL

- Chain: `0020_wagle_message_reactions -> 0021_board_room_race_hardening`
  is a single head; `down_revision` is correct. Fresh disposable PostgreSQL
  successfully ran `0020 -> 0021 -> 0020 -> 0021`.
- Invariant: correct partial unique index,
  `wagle_rooms(family_group_id)` where GROUP + `__family_board__` +
  `deleted_at IS NULL`; two ordinary GROUP rooms with the same title inserted
  successfully. Family-B control remained one active board.
- Basic preservation observed: 3 messages were retained and renumbered 1..3;
  the reaction survived; downgrade drops the index only and re-upgrade works.
- **Blocking defect:** merge does not preserve an active participant in every
  valid duplicate shape. In a synthetic Family A, the canonical room had a
  `left` row for membership 1; a losing room had an older `left` row followed
  by that membership's `active` row. `_merge_duplicate_board_rooms()` selects
  the earliest loser candidate without filtering it to active, moves the
  `left` row to canonical, remaps/deletes the active row, and leaves no active
  participant for membership 1. Direct post-upgrade query returned
  `membership 1: left=2, active=0`; its active-room message was retained.
  This violates the migration's own stated active-membership preservation
  contract and can remove board access/read-state semantics despite content
  surviving.

## Board room concurrency / Admin auth

- Existing actual API-boundary concurrency regression passed: 5 concurrent
  requests × 10 fresh Families, all 201/same room ID/final active count 1
  (included in focused result below). Code has server lookup, unique-conflict
  rollback/refetch, and the DB invariant.
- `backend/tests/test_auth_admin_login.py` passed through the API boundary:
  >72-byte ASCII, >72-byte UTF-8 Korean, unknown username + long input all
  fail closed; normal login succeeds. No bcrypt exception/500 was observed.
- Focused command on fresh disposable DB:
  `pytest -q tests/test_wagle_integration.py tests/test_auth_admin_login.py tests/test_w75_phase_d_board_reactions.py`
  → **39 passed** (45.62 s); this also covers Popular Posts.

## E2E runner / artifacts — FAIL

The runner has genuine query readiness, `ON_ERROR_STOP=1`, table assertion,
Alembic retry, synthetic password, and cleanup trap. However it redirects the
temporary backend/frontend logs to `/tmp/mc_w75_spec_runner_*.log`.
`AGENTS.md`/`rules.md` prohibit agent-created project artifacts outside the
worktree, and `tests/README.md` explicitly says not to run/update such a
workflow until its output is moved inside the worktree. Therefore the required
README-only four back-to-back invocations were **not authorized/executed**;
10/10 × 4, cleanup, and post-run Git-artifact claims are unverified. Static
artifact audit: `.last-run.json` is staged for deletion from the index and is
ignored by `.gitignore`; no runner execution was performed to establish its
runtime behavior.

## Backend and static checks

On one separate disposable PostgreSQL (port 15435, init.sql then Alembic head):

```text
collect-only: 389
Run 1: 389 passed, 1 warning, 365.77 s
Run 2: 389 passed, 1 warning, 367.96 s
```

Backend import (synthetic JWT), frontend typecheck, eslint, Vite build, and
`git diff --check` passed. `check_all.py` exited 0 but emitted pre-existing
registry/closeout warnings, including a target-task handoff/QA discovery
warning; no W7.5-specific checker warning was measured as newly caused here.

## Findings

### HARDENING-QA-F-001

```text
Severity: HIGH
Category: PRODUCT_DEFECT / data migration
File: backend/alembic/versions/0021_board_room_race_hardening.py
Evidence: active participant becomes absent in canonical after 0021.
Reproduction: canonical has membership M left; loser has older M left plus
  newer M active; upgrade 0020 -> 0021; query active participants in canonical.
Impact: existing board member can lose active participation/access semantics
  during duplicate consolidation.
Required remediation: choose/promote an active loser candidate when no active
  canonical survivor exists; add a migration-level regression covering this
  state and re-run lossless merge/round-trip independent QA.
```

### HARDENING-QA-F-002

```text
Severity: MEDIUM
Category: TEST_INFRASTRUCTURE / policy compliance
File: tests/e2e/scripts/run-w75-full-spec.sh
Evidence: hard-coded redirects to /tmp/mc_w75_spec_runner_backend.log and
  /tmp/mc_w75_spec_runner_frontend.log.
Impact: required four-run independent reproduction cannot be run under the
  repository-boundary contract; E2E repeatability and artifact cleanliness are
  not established.
Required remediation: put ephemeral logs in an ignored, policy-approved path
  inside the worktree, then independently run the documented command 4 times.
```

## 5-gate result

```text
Hallucination Guard: PASS — current source and disposable execution used.
Omission Guard: FAIL — active-participant merge edge case found.
Miswork Guard: PASS — no product/test/migration/seed modification.
Axis Alignment: PASS — no claim of W7.5 overall PASS or W7.6 readiness.
Freshness/Evidence Consistency: PASS — current HEAD and fresh DBs recorded.
```

No PASS declaration is valid. W7.5 overall remains CONDITIONAL/HUMAN_GATE;
W7.4 remains REOPENED/audit pending; W7.6 remains blocked.
