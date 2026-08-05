# QA Evidence — MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-FOCUSED-INDEPENDENT-QA-001

- Task ID: `MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-FOCUSED-INDEPENDENT-QA-001`
- author/agent: independent QA session (fresh session, did not author the diff under review)
- observed_at: 2026-08-05
- git_ref: real repo HEAD `0a1bde1` (branch `dev-newmarkp`) + the real working tree's own
  uncommitted 2-file diff (`backend/app/domains/wagle/service.py`,
  `backend/tests/test_wagle_permission_role_cardinality.py`), reconstructed byte-identically
  in a detached scratch worktree at the same `0a1bde1` base
- environment: macOS (OrbStack/Docker Desktop), isolated `postgres:16.9-alpine` on port 15447
  (own container, `mc_qa_wagle_cardinality_db`, distinct from the developer's own port 15446/15435
  containers, both already gone) for reproduction + pytest; shared `mongle-backend-1`/`mongle-db-1`
  (`docker-compose.phase1.yml -p mongle`, ports 18001/15434) for real-login curl smoke only, used
  read/insert-then-delete, never restarted
- evidence: this file + the Session Handoff at
  `agent-system/handoffs/active/MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-FOCUSED-INDEPENDENT-QA-001.md`
- secrets_redacted: `true`
- Verification: `PASS`
- Verdict: PASS
- Closeout Contract: `v1`
- Independent from implementer: `true`
- Independent QA: `complete`

## Independent QA qualification

Fresh session. Did not author `MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001`'s diff.
Per `agent-system/rules.md` Invariant 9, checked before opening this Task ID: grepped
`active.md`/`relay/current.md`/`agent-system/qa/COVERAGE_MAP.md` for
`WAGLE-MULTI-ROLE-CARDINALITY` — only the `-REMEDIATION-001` entry exists (it names this QA
task as its own required next step, not yet done), so this is legitimately new, not a duplicate.
All runtime evidence below (isolated pytest DB, isolated A/B revert, live curl matrix) was
independently produced in this session's own scratch worktree/containers, not copied from the
developer's own claimed numbers — the developer's own claimed counts (411/411, 6/6, etc.) are
cited only where this session's own independently-measured number matches them.

## Scope reviewed

`backend/app/domains/wagle/service.py::_require_permission`'s READ retained-access check
(1-line diff: `.limit(1)` appended to an existing `scalar_one_or_none()` query) and the new
`backend/tests/test_wagle_permission_role_cardinality.py` (6 tests). No other file in the real
repo's diff. Read-only for all product code — no edit made in the real repo's working tree at
any point; the one intentional revert-then-restore used for A/B evidence was performed only in
this session's own detached scratch worktree, confirmed byte-identical to the real repo's diff
both before the revert and after restoration.

## Isolated execution copy construction

1. `git -C /Users/mac/mac_Project/mongle_ui worktree add --detach /Users/mac/mac_Project/mongle_ui_qa_scratch 0a1bde1`
2. Copied the real repo's current `backend/app/domains/wagle/service.py` and
   `backend/tests/test_wagle_permission_role_cardinality.py` into the scratch worktree.
3. Verified: scratch `git status --short` showed exactly those 2 files (1 modified, 1
   untracked); `git diff HEAD -- backend/app/domains/wagle/service.py` in the scratch worktree
   was byte-identical (`diff` exit 0) to the same command in the real repo.
4. Ran all pytest/reproduction work from this Target Revision. Removed via
   `git worktree remove --force` at teardown; confirmed gone from `git worktree list`.

## Commands, exit codes, and results

| Command | Result |
|---|---|
| `alembic upgrade head` against a fresh `mc_qa_wagle_cardinality_db` (port 15447), after `database/init.sql` | 21 migrations applied cleanly, `0000`→`0021` |
| `pytest tests/test_wagle_permission_role_cardinality.py -v` (Target Revision) | **6 passed**, 0 failed |
| Registry check after the 6 tests | `roles`=9, `role_permissions`=29 (baseline, confirmed via direct `SELECT count(*)`) — the test-scoped synthetic role in `test_three_roles_...` was deleted in its own `finally`, no leak |
| A/B: reverted `.limit(1)` in the scratch copy only (temporary, own worktree, never the real repo), re-ran the same file | **2 failed** (`test_two_roles_...`, `test_three_roles_...`), both with `sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required`, traceback rooted at `wagle/service.py:77`'s `scalar_one_or_none()` via `wagle/router.py::list_rooms` → `service.list_rooms` → `_require_permission` — the other 4 tests (single-role/no-permission/no-membership/cross-family) still passed, unaffected |
| Restored `.limit(1)`; `diff` against the real repo's `backend/app/domains/wagle/service.py` | exit 0, byte-identical — scratch copy confirmed back to the real Target Revision before any further work |
| Full backend suite: `pytest -q` (Target Revision, same isolated DB, fresh from the `.limit(1)` restore) | **411 passed, 0 failed, 1 warning (unrelated Pydantic deprecation), 439.64s** |
| `pytest tests/test_wagle_reliable_service_slice.py::test_outbox_07_two_workers_no_double_claim -v` (standalone, immediately after the full-suite run) | **1 passed** — `KNOWN-W7-5-WAGLE-CONCURRENCY-001` did **not** manifest in either the full-suite run or this standalone re-run; a clean run is itself sufficient evidence per that row's own registration, no A/B needed |
| Live curl, shared `mongle-backend-1` (confirmed serving byte-identical Target Revision source, see below), real `POST /api/auth/account/login` with a disposable Account-native credential holding 2 READ-granting roles (`participant`+`room_admin`) on membership id 7 (family 1) | `200`, real access token issued |
| `GET /api/families/1/wagle/rooms` with that real token | `200`, body `[]` (empty room list is correct — the disposable membership has no `WagleParticipant` row in any room; the point under test is the 200/no-500, not room contents) |
| Same request with **no** `Authorization` header | `401 {"detail":"인증이 필요합니다"}` |
| Same real 2-role token against `GET /api/families/2/wagle/rooms` (a family this account has no membership in) | `403 {"detail":"활성 가족 구성원 권한이 필요합니다"}` |
| `git diff --check` (real repo) | exit 0 |
| `git diff --check` (scratch worktree, post-restore) | exit 0 |
| `python3 agent-system/tools/check_all.py` (real repo, report-only) | ran clean; all WARNINGs shown pre-date this task (other tasks' own known gaps — `NATIVE-E2E-...`, `MONGLE-W1-...`, etc.); 0 new warning attributable to this diff or this QA task |

## Findings

### Root cause verification

Independently confirmed, not merely re-cited: `scalar_one_or_none()` raises
`sqlalchemy.exc.MultipleResultsFound` for 2+ rows (proven by my own A/B revert above, both at
the pytest/HTTP level). Migration `0002_doran_messaging_foundation.py` (later renamed
`doran`→`wagle` by migration `0007_wagle_runtime_identifiers`, independently confirmed by
reading that migration's own docstring and rename table) seeds exactly two `SERVICE/wagle`
roles — `participant` and `room_admin` — and grants both `wagle.messages.read` (and
`wagle.messages.send`). Nothing in the schema prevents one membership from holding both roles
simultaneously (`uq_active_membership_role`, migration `0001`, only blocks the *same* role
twice — independently confirmed live by triggering it: attempting to grant `participant` a
second time to a membership that already has it raises a unique-violation; granting the
*distinct* `room_admin` role does not). A membership with both active roles therefore made the
retained-READ query legitimately return 2 rows, and the un-limited `scalar_one_or_none()`
crashed instead of answering "yes, retained."

### Authorization semantics

Read the full function body (`_require_permission`, lines 62-80) directly, not just the diff
hunk. Confirmed: (1) the only use of the query's result is `if retained is not None: return` —
no caller of `_require_permission`, and no code anywhere in `wagle/service.py`, reads any other
attribute of the matched row (the query only ever selected `Permission.id`, and even that value
itself is discarded — only its non-nullness matters); (2) `.limit(1)` has no `ORDER BY`, so
which of the 2+ matching rows Postgres happens to return is unspecified/non-deterministic across
runs — but since only existence is checked, this is provably immaterial to the authorization
outcome; (3) the `WHERE` predicate (`membership_id`, `revoked_at IS NULL`, `Role.is_active IS
TRUE`, `Permission.code == READ`) is byte-identical before and after the diff — revocation and
active-role filtering are preserved exactly; (4) family scope is preserved structurally, not by
this query directly — `membership` is already resolved by `context()` →
`family_service.get_active_membership(db, account.id, family_id)` before `_require_permission`
is ever called, so a membership object can only belong to the family it was resolved against;
independently confirmed by the live cross-family curl check above returning 403 for a real
2-role account against a family it has no membership in. (5) `SEND`/`CREATE`/`MANAGE_ROOM`/
`MANAGE_PARTICIPANTS` never enter the `if code == READ:` branch at all (confirmed by reading the
function's control flow) — they fall straight through to
`family_service.effective_permissions(db, membership)`, independently read and confirmed to be
already row-set-based (`.all()` collected into a `Set[str]`, `family/service.py` lines 235-250)
and therefore structurally immune to this exact defect shape, both before and after this diff.
This diff changes 0 lines outside the `if code == READ:` block.

### Role 1/2/3 results

| Case | Method | Result |
|---|---|---|
| 1 role granting READ (regression) | pytest, real HTTP request through the ASGI app, legacy-identity JWT (`tests/conftest.py`'s established `create_actor`/`make_token` pattern — a real `player`→`Account` bridge via `LegacyIdentityMapping`, resolved through the real `resolve_current_account`/`get_active_membership` dependency chain, not a function call) | `200` |
| 2 roles, both granting READ (`participant`+`room_admin`) | pytest (legacy identity, as above) **and** live curl real login (Account-native identity: real `POST /api/auth/account/login` → real JWT → `GET .../wagle/rooms`) | `200` in both; no 500 in either |
| 3 roles, all granting READ (2 real + 1 test-scoped synthetic role, deleted after) | pytest (legacy identity) only — not additionally re-verified via live real-login curl this session, since `uq_active_membership_role` and the "only 2 real Wagle roles exist" constraint make constructing a genuine 3rd distinct role on the shared live stack materially riskier (a 3rd real registry row would need cleanup on shared, not disposable, `roles`/`role_permissions` tables) for no additional defect-coverage value beyond what the isolated pytest case already proves | `200`, no 500 |

Both identity models (Account-native and legacy-player-via-bridge) were directly exercised, not
only cited: the live curl matrix is genuinely Account-native (a real `account_credentials` row,
real bcrypt-verified login); the pytest suite's `family_env`/`create_actor` fixtures are
genuinely legacy (real `Player`/`PlayerAuth` rows bridged through a real
`LegacyIdentityMapping`, decoded via the real `role: "player"` JWT path) — both go through the
real HTTP/ASGI request cycle and the real `_require_permission` code path, not a direct function
call.

### Denial results

| Case | Method | Result |
|---|---|---|
| Active membership, no role grants any Wagle permission | pytest (`test_role_without_the_permission_denied`) | `403` |
| No membership for the requested family at all | pytest (`test_no_membership_denied`) | `403` |
| Unauthenticated | live curl, no `Authorization` header, shared stack | `401` |

### Cross-family security

An account whose own membership legitimately holds 2 READ-granting roles was independently
confirmed still denied for a family it is not a member of, via **two independent methods**:
pytest (`test_cross_family_duplicate_role_membership_still_scoped_to_its_own_family`, legacy
identity) and live curl (Account-native identity, the same disposable dual-role account from the
Role-2 case above, `GET /api/families/2/wagle/rooms` → `403`). The duplicate-role fix does not
create or widen any cross-family leak.

### Wagle regression coverage

Required list, with method stated per row (directly exercised this session vs. cited from an
existing, independently-run passing test):

| Journey | Directly exercised this session? | Evidence |
|---|---|---|
| Room list (`list_rooms`) | **Yes** | New pytest 6/6 (legacy identity) + live curl 2-role/401/403 matrix (Account-native identity), both above |
| Room list w/ preview + unread count (`list_rooms_with_preview`, `/room-summaries`) | No — cited | Same `_require_permission(READ)` call site; covered by `API-W2-WAGLE-ROOM-SUMMARY-001` (`test_wagle_durable_wave2.py`), independently re-run by me as part of the 411/411 full-suite pass above, not isolated separately this session |
| Message list (`list_messages`) | No — cited | Same call site; covered by `API-W2-WAGLE-ORDERING-READ-001` (`test_wagle_durable_wave2.py`), independently re-run as part of the same 411/411 pass |
| Message send (`send_message`) | No — cited | Routes through `SEND`, which never enters the fixed branch at all (confirmed by code read above); covered by `API-W2-WAGLE-DURABLE-001` (`test_wagle_durable_wave2.py`), independently re-run as part of the 411/411 pass |
| Room binding (`onboard_self_into_service_room`, service-principal binding flows) | No — cited | `onboard_self_into_service_room` shares the same `_require_permission(READ)` call site; covered by `test_wagle_service_binding.py`, independently re-run as part of the 411/411 pass |
| Account-native user identity | **Yes** | Live curl matrix: real `account_credentials` row, real `POST /api/auth/account/login`, real JWT (`role: "account"`) |
| Legacy user identity | **Yes** | pytest 6/6: `create_actor`'s real `Player`/`PlayerAuth`/`LegacyIdentityMapping` bridge, real `role: "player"` JWT |
| Family permission boundary (cross-family denial) | **Yes** | Both pytest and live curl, see Cross-family security above |
| Admin permission boundary (Wagle's own privileged `room_admin` role vs. plain `participant`; `CREATE`/`MANAGE_ROOM`/`MANAGE_PARTICIPANTS`) | No — cited | These codes never enter the fixed `if code == READ:` branch (confirmed by code read); covered by `test_wagle_integration.py`'s existing `room_admin`-vs-`participant` boundary tests, independently re-run as part of the 411/411 pass. Not re-isolated individually this session since they are structurally unreachable by this exact defect. |

Full backend suite result underlying every "cited" row above: **411 passed, 0 failed**,
independently executed by this session end-to-end (not re-stated from the developer's own
number, though it matches).

### Frontend

Explicit decision: **`pnpm lint`/`pnpm run build` NOT re-run this session.** Reasoning: the
diff under review touches exactly 2 backend files (confirmed via `git status --short` and `git
diff HEAD --stat` on both the real repo and the byte-identical scratch copy) — zero frontend
files. A backend-only permission-check fix has no code path into the frontend build/lint
pipeline; re-running it would not exercise any changed line and would only re-confirm frontend
state this task did not touch. This is a stated decision, not a silent skip.

### DB safety

| Resource | Action | Final state |
|---|---|---|
| `mc_qa_wagle_cardinality_db` (own isolated container, port 15447) | created, used for `alembic upgrade head` + all pytest work (including the A/B revert-and-restore), removed (`docker rm -f`) | container gone, confirmed via `docker ps -a` |
| Scratch worktree `/Users/mac/mac_Project/mongle_ui_qa_scratch` | created, used as the Target Revision execution copy, removed (`git worktree remove --force`) | confirmed gone from `git worktree list`; real repo now shows only its own worktree |
| Stray empty directory `/Users/mac/mac_Project/mongle_ui_scratch_qa` (created by an earlier mistyped path in this session, never used) | removed (`rmdir`) | gone |
| Live shared DB (`mongle-db-1`, `mc_festival_phase0`): `accounts` id=7, `account_credentials` id=5, `family_memberships` id=7, `membership_role_assignments` ids=14,15, `account_sessions` id=21 | inserted (disposable Account-native QA fixture), all deleted in FK-safe order after use | independently re-verified: `accounts`=6, `account_credentials`=4, `family_memberships`=6, `membership_role_assignments`=11, `family_groups`=2 — **exactly matches the pre-insert baseline** measured by this session before any insert |
| Test-scoped synthetic role `qa_cardinality_extra_reader_001` (isolated pytest DB only, created inside `test_three_roles_granting_the_same_permission_no_500`'s own `try`) | deleted in its own `finally` | independently confirmed 0 rows remaining (`roles`=9, `role_permissions`=29, matching the pre-test baseline) both immediately after the isolated test file run and again after the full 411-test suite run |
| Shared stack (`mongle-backend-1`/`mongle-db-1`) | read + insert/delete only, never rebuilt, never restarted | confirmed still running the same Target Revision source throughout (re-checked via `docker exec ... cat service.py`, byte-identical to the Target Revision both times checked) |

No product code was ever edited in the real repo's working tree. The one code revert used for
A/B evidence was made and restored only inside the disposable scratch worktree, which no longer
exists.

## Final QA verdict

**PASS.** This is genuinely independent verification (fresh session, no shared authorship with
`MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001`), backed by this session's own
executed A/B reproduction (pre-fix `MultipleResultsFound` independently reproduced and
post-fix absence independently confirmed, not merely re-cited from the developer's own claim),
this session's own 6/6 new-test run, this session's own 411/411 full-suite run (including a
clean pass of the `KNOWN-W7-5-WAGLE-CONCURRENCY-001` test both in-suite and standalone), and
this session's own real-login curl matrix against a verified-matching live stack. The fix is a
1-line, existence-check-only change (`.limit(1)`, no `ORDER BY`, no downstream attribute usage)
that does not alter which memberships are granted retained READ access, does not touch any
non-READ permission code path, and preserves revocation/active-role filtering and family
scoping exactly. All QA-created DB rows (isolated and live-shared) were insert-only and fully
deleted, independently re-verified against this session's own measured pre-task baseline. All
scratch containers/worktrees torn down.

## Closeout review

- ACTIVE: `UPDATED`
- HANDOFF: `UPDATED`
- QA EVIDENCE: `UPDATED` (this file)
- COVERAGE MAP: `UPDATED` (append-only note on the existing `API-W7-4-WAGLE-MULTI-ROLE-
  CARDINALITY-001` row's own Notes field, confirming independent re-verification; no existing
  cell rewritten)
- COVERAGE MAP Reason: execution evidence changed — the row's Verification/Confidence moves from
  "Developer self-check" only to independently re-confirmed
- CLOSEOUT GATE: `PASS`
