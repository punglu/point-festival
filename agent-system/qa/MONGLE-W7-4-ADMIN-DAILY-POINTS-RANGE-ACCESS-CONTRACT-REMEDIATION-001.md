# QA Evidence — MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001

Developer self-check (this task modified product code — Independent QA PASS not self-declared; see `DEVELOPER_SELF_CHECK_COMPLETE` in the handoff).

Full narrative, root cause, and the exact diff are in
`agent-system/handoffs/active/MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001.md`.
This file is the compact evidence table.

## Environment

- Runtime: `docker-compose.phase1.yml -p mongle` (DB 15434, backend 18001) rebuilt from `281d45a` + this change; frontend served natively (`pnpm run dev`, :5174) since the official container frontend build fails independently (`npm ci` / npm→pnpm migration mismatch, pre-existing, out of scope, already logged in the prior runtime-completion QA)
- Backend pytest: isolated `postgres:16.9-alpine` (port 15435) + `alembic upgrade head` + `database/init.sql`, torn down after use

## Result matrix

| Check | Identity | Expected | Actual |
|---|---|---|---|
| `GET /api/admin/daily-points/range` | Account-native Admin | 200 | 200 |
| " | legacy Admin | 200 | 200 |
| " | legacy Admin, null `player_id` | 200 | 200 |
| " | legacy player | 401/403 | 401 |
| " | non-Admin Account | 401/403 | 401 |
| " | unauthenticated | 401 | 401 |
| `GET /api/daily-points/range` (existing, unchanged) | player, self | 200 (regression) | 200 |
| " | player, other player_id | 403 (regression) | 403 |
| " | Account-native Admin | unchanged (still 403) | 403 |
| `GET /api/admin/daily-points` (existing) | legacy Admin | 200 (regression) | 200 |
| `GET /api/account-context` | legacy Admin, null `player_id` | 403 `mapping_required` (regression) | 403 `mapping_required` |
| AdminDashboard `/admin`, "플레이어 현황" card | Account-native Admin | shows real `earned` sum, not `0pt` | `15pt` shown after a real `+15` adjust, holds across reload |
| AdminDashboard `/admin` | legacy Admin | same | `15pt` shown |
| Viewport 390×844 / 820×1180 / 1180×820 | Account-native Admin | renders, no overflow | PASS all 3 |

## Static / build / test

| Check | Result |
|---|---|
| `pnpm lint` | 0 issues |
| `pnpm run build` (`tsc -b && vite build`) | passed, 0 new TS errors |
| `git diff --check` | exit 0 |
| `python3 agent-system/tools/check_all.py` | same warning set as baseline, 0 new |
| Backend pytest, full suite | 404 passed, 1 failed (`test_wagle_reliable_service_slice.py::test_outbox_07_two_workers_no_double_claim` — pre-existing `KNOWN-W7-5-WAGLE-CONCURRENCY-001`, see Coverage Map; confirmed present identically on unmodified `281d45a` via `git stash`, confirmed *not* worsened by this change on 2 repeat runs with the change restored) |

## DB safety

| Row | Action | Final state |
|---|---|---|
| `admin_auth.qa_marker_null_player_admin_range_fix` (`player_id=NULL`) | inserted, used for the null-player-Admin row above, deleted | `admin_auth` = 2 rows (baseline: `dad`, `mom`) |
| `daily_points` (`player_id=3`, `2026-08-03`, `earned=15`) | created via the pre-existing `/api/admin/daily-points/adjust` to prove real data flows through, deleted | `daily_points` = 0 rows (baseline) |
| `mc_phase2_qa_db` (ad hoc pytest Postgres, port 15435) | created, fully removed | container gone |

## Verdict

`DEVELOPER_SELF_CHECK_COMPLETE`. Recommend `MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-001` as the next task.
