# QA Evidence — MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001

Developer self-check (this task modified product code — Independent QA PASS not self-declared; see `DEVELOPER_SELF_CHECK_COMPLETE` in the handoff).

Full narrative, root cause, and the exact diff are in
`agent-system/handoffs/active/MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001.md`.
This file is the compact evidence table.

## Environment

- Reproduction: isolated `postgres:16.9-alpine` (`mc_wagle_qa_db`, port 15446) + `database/init.sql` + `alembic upgrade head`, `backend/.venv` (Python 3.11.15)
- pytest (new tests + full suite): isolated `postgres:16.9-alpine` (`mc_phase2_qa_db`, port 15435, matching `tests/conftest.py`'s own default DSN)
- Live curl + Playwright smoke: shared `mongle-backend-1`/`mongle-db-1` (`docker-compose.phase1.yml -p mongle`, rebuilt with this fix), frontend served natively (`pnpm run dev`, :5174) with a temporary CORS override, reverted after use

## Reproduction (A/B)

| Run | Code state | Result |
|---|---|---|
| 1 | pre-fix (original `scalar_one_or_none()`, no `.limit(1)`) | `sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required` — function call and real HTTP request (`GET /api/families/{id}/wagle/rooms`) both |
| 2 (A) | pre-fix, re-confirmed via the 2 new pytest cases | `test_two_roles_granting_the_same_permission_no_500` and `test_three_roles_granting_the_same_permission_no_500` both FAIL with the identical exception; the other 4 new tests (single-role/denial/no-membership/cross-family) PASS unaffected |
| 3 (B) | fix restored (`.limit(1)`) | same 2 tests PASS; all 6 PASS |

## Result matrix

| Check | Identity/Shape | Expected | Actual |
|---|---|---|---|
| `_require_permission(READ)`, 2 roles both granting READ | fixture membership | no exception | no exception |
| `_require_permission(READ)`, 1 role granting READ | fixture membership | no exception (regression) | no exception |
| `GET /wagle/rooms`, 2 roles (`participant`+`room_admin`) | pytest `family_env["member"]` + granted `room_admin` | 200 | 200 |
| `GET /wagle/rooms`, 3 roles (2 real + 1 test-scoped synthetic, all granting READ) | pytest fixture | 200 | 200 |
| `GET /wagle/rooms`, role with no Wagle permission | pytest `create_actor(service_role=None)` | 403 | 403 |
| `GET /wagle/rooms`, no membership in this family | pytest, actor from a different family | 403 | 403 |
| `GET /wagle/rooms`, own membership has 2 READ roles but wrong family | pytest, cross-family | 403 | 403 |
| `GET /api/families/1/wagle/rooms`, live shared stack, real `member.a` login, real 2nd `room_admin` DB row | live curl | 200 | 200, real room JSON |
| `/wagle` real browser navigation, `member.a` (2 roles) | live Playwright | network 200, no console 500 | PASS |

## Static / test gates

| Check | Result |
|---|---|
| `git diff --check` | exit 0 |
| `python3 agent-system/tools/check_all.py` | same warning set as baseline, 0 new |
| New pytest (`tests/test_wagle_permission_role_cardinality.py`) | 6/6 PASS |
| Full backend pytest suite | 411 passed, 0 failed (405 baseline + 6 new); `KNOWN-W7-5-WAGLE-CONCURRENCY-001` did not manifest this run |
| `pnpm lint` / `pnpm run build` | not re-run — no frontend file touched by this diff; already verified clean earlier this session on the same working tree |

## DB safety

| Row/resource | Action | Final state |
|---|---|---|
| `mc_wagle_qa_db` (isolated, port 15446) | created, used for initial reproduction, removed | container gone |
| `mc_phase2_qa_db` (isolated, port 15435) | created, used for all pytest, removed | container gone |
| `membership_role_assignments` id=12 (live shared DB, first curl smoke) | inserted, deleted | — |
| `membership_role_assignments` id=13 (live shared DB, Playwright smoke) | inserted, deleted | — |
| live shared DB wagle role assignments | — | back to exactly 2 rows (`Synthetic Owner A`→`room_admin`, `Synthetic Service Participant`→`participant`), matching pre-check baseline |
| test-scoped synthetic role `qa_cardinality_extra_reader_001` (pytest DB only) | inserted + used inside one test's `try`, deleted in its own `finally` | confirmed 0 rows remaining after the suite run |
| `mongle-backend-1` CORS | temporarily widened to include `:5174` for the Playwright smoke, reverted (`5174` origin now `400` again, `13001` still `200`) | back to original |

## Verdict

`DEVELOPER_SELF_CHECK_COMPLETE`. Recommend `MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-FOCUSED-INDEPENDENT-QA-001` as the next task.
