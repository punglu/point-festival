# MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001

- Task ID: `MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001`
- Branch: `dev-newmarkp`
- Start HEAD: `0a1bde1` (clean, `local == origin/dev-newmarkp`)
- End HEAD: unchanged (`0a1bde1`) — no commit/push, per this task's own constraints
- Scope: fix a `MultipleResultsFound` → HTTP 500 in Wagle's permission check when a membership holds 2+ roles that each grant the same permission. Out of scope: Wagle UI redesign, role/permission model changes, DB migrations, Admin daily-points, `frontend/Dockerfile`, Auth/Family/Markpoint QA, W7.6.

## Baseline

`pwd /Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`, HEAD `0a1bde1`, `git status --short` empty, `git diff --check` exit 0, `git stash list` empty, `git log -5` confirms `0a1bde1` (docs) → `48ad2cc` (admin daily-points range) → `281d45a` (DEFECT-001/002) → `97bc09d` → `0319940`. Matches the task's stated candidate baseline exactly.

## Reproduction (before any code change)

Root cause located via `grep` for cardinality-assuming queries in `backend/app/domains/wagle/service.py` and `backend/app/domains/family/service.py`. Found in `wagle/service.py::_require_permission` (lines 62-70), the special-cased "retained READ access" check:

```python
if code == READ:
    retained = (await db.execute(select(Permission.id).join(...).where(
        MembershipRoleAssignment.membership_id == membership.id,
        MembershipRoleAssignment.revoked_at.is_(None),
        Role.is_active.is_(True),
        Permission.code == READ,
    ))).scalar_one_or_none()
```

`migration 0002_doran_messaging_foundation.py` (line 40) seeds **both** `participant` and `room_admin` (the only two `SERVICE/wagle` roles that exist) to grant `wagle.messages.read`/`wagle.messages.send`. A membership holding both roles simultaneously (a fully realistic, unprevented combination — see Authorization Semantics below) makes this query return 2 rows; `scalar_one_or_none()` requires 0 or 1 and raises `MultipleResultsFound` for 2+.

Reproduced twice before fixing, in an isolated Postgres (`mc_wagle_qa_db`, port 15446, `database/init.sql` + `alembic upgrade head`, `backend/.venv` on Python 3.11):

1. **Function level** — direct call to `wagle_service._require_permission(db, membership, wagle_service.READ)` against a fixture membership holding both `participant` and `room_admin`:
   `RESULT: EXCEPTION sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required`
2. **HTTP level** — real `/api/auth/account/login` → real JWT → `GET /api/families/1/wagle/rooms` (via `httpx.ASGITransport` against `app.main.app`, the same in-process pattern `tests/conftest.py` already uses): the identical `MultipleResultsFound` propagates unhandled through `wagle/router.py::list_rooms` → `wagle/service.py::list_rooms` → `_require_permission`. In a real deployed server this becomes an HTTP 500 (Starlette's default unhandled-exception path / this repo's own global handler, per `P7-SEC-003`); `ASGITransport` re-raises to the caller by default rather than converting it, which is why the script sees the raw traceback instead of a 500 response object.

## Confirmed Root Cause

`_require_permission`'s READ-retained-access check assumed at most one matching row, but the seed data (migration 0002) intentionally grants the same permission from two different roles, and nothing in the schema prevents a membership from holding both at once.

## Authorization Semantics

The check's actual intent, read directly from its own comment ("Retained read access deliberately does not disappear merely because the Wagle subscription became suspended/cancelled"), is a pure **existence** question — "does any currently-active role grant READ" — not a lookup of a specific row's identity or attributes. No caller uses which specific role matched; only `is not None` is checked afterward.

## Changed Files

- `backend/app/domains/wagle/service.py` — one line: append `.limit(1)` to the retained-READ query, so its cardinality contract now matches what `scalar_one_or_none()` actually promises to handle (0 or 1 row), for any number of matching roles (2, 3, ...). No other line touched; no change to which memberships are granted retained access, to `effective_permissions` (already row-set-based via `.all()`, confirmed safe — not part of this bug), or to any denial path.
- `backend/tests/test_wagle_permission_role_cardinality.py` — new, 6 tests (see Validation).

```diff
--- a/backend/app/domains/wagle/service.py
+++ b/backend/app/domains/wagle/service.py
@@ -63,8 +63,17 @@ async def _require_permission(db: AsyncSession, membership: FamilyMembership,
     # Retained read access deliberately does not disappear merely because the
     # Wagle subscription became suspended/cancelled.
     if code == READ:
-        retained = (await db.execute(select(Permission.id).join(RolePermission, RolePermission.permission_id == Permission.id).join(Role, Role.id == RolePermission.role_id).join(MembershipRoleAssignment, MembershipRoleAssignment.role_id == Role.id).where(MembershipRoleAssignment.membership_id == membership.id, MembershipRoleAssignment.revoked_at.is_(None), Role.is_active.is_(True), Permission.code == READ))).scalar_one_or_none()
+        # MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001: this is an
+        # existence check ("does any currently-active role grant READ"), not a
+        # lookup of a specific row -- a membership legitimately holding 2+
+        # roles that each grant `wagle.messages.read` (e.g. `participant` and
+        # `room_admin` both do, per migration 0002) made this query return
+        # more than one row, and `scalar_one_or_none()` raised
+        # `MultipleResultsFound` (uncaught -> HTTP 500) instead of the
+        # intended "yes, retained" answer. `.limit(1)` makes the cardinality
+        # match what `scalar_one_or_none()` actually promises to handle,
+        # without changing which memberships are granted retained access.
+        retained = (await db.execute(select(Permission.id).join(RolePermission, RolePermission.permission_id == Permission.id).join(Role, Role.id == RolePermission.role_id).join(MembershipRoleAssignment, MembershipRoleAssignment.role_id == Role.id).where(MembershipRoleAssignment.membership_id == membership.id, MembershipRoleAssignment.revoked_at.is_(None), Role.is_active.is_(True), Permission.code == READ).limit(1))).scalar_one_or_none()
         if retained is not None:
             return
```

## A Real, Pre-existing Constraint Discovered During Fixture Construction

`uq_active_membership_role` (migration `0001_account_family_rbac_foundation.py`, a partial unique index on `(membership_id, role_id) WHERE revoked_at IS NULL`) prevents assigning the *same* role twice to one membership while active — confirmed by triggering it directly (`UniqueViolationError`) while building the "3 roles" test fixture. Combined with only 2 real `SERVICE/wagle` roles existing that grant READ, a genuine 3rd *duplicate-permission* row requires a 3rd *distinct* role; the test creates one, scoped and named for the test only, and deletes it (role + role_permissions link) in a `finally` so the untruncated `roles`/`role_permissions` registry tables are not left polluted for later tests in the same pytest session.

## Duplicate-role Results (pytest + live curl + live Playwright)

| Case | Expected | Result |
|---|---|---|
| 1 role has permission (regression) | allow | PASS |
| 2 roles, same permission (`participant` + `room_admin`) | allow, no 500 | PASS |
| 3 roles, same permission (+ 1 test-scoped synthetic role) | allow, no 500 | PASS |
| Live shared stack (`mongle-backend-1`, real DB row: `member.a`'s real membership granted a real 2nd `room_admin` assignment, deleted after) — `GET /api/families/1/wagle/rooms` via real login | 200 | 200, real room data returned |
| Real browser (Playwright, disposable spec, deleted after use) — `member.a` navigates to `/wagle` | network response 200, no console 500 | PASS |

## Denial Results

| Case | Expected | Result |
|---|---|---|
| Role assigned, but grants no Wagle permission (no `service_role` at all) | 403 | PASS |
| No membership for the requested family at all | 403 | PASS |
| Unauthenticated (pre-existing, unaffected by this diff) | 401 | unaffected — not re-verified in isolation here; already covered by `test_wagle_integration.py::test_01a_*`, which this diff does not touch |

## Cross-family Security

An actor whose *own* membership (in a different Family) legitimately holds 2 READ-granting roles still gets 403 against a Family it is not a member of — the duplicate-role fix does not create any cross-family leak (`test_cross_family_duplicate_role_membership_still_scoped_to_its_own_family`, PASS).

## Regression

- Full backend pytest suite: **411 passed, 0 failed** (405 previous baseline + 6 new). `KNOWN-W7-5-WAGLE-CONCURRENCY-001` (`test_wagle_reliable_service_slice.py`, registered intermittent condition) did not manifest this run — no A/B needed since nothing failed.
- `pnpm lint` / `pnpm run build`: not re-run — this diff touches no frontend file; both were already verified clean earlier in this session against the same `dev-newmarkp` working tree.
- `git diff --check`: exit 0. `check_all.py`: same warning baseline, 0 new.
- Live smoke via the shared `mongle-backend-1` stack: `/api/admin/*`, `/api/account-context` 403 `mapping_required`, and Admin access (all verified in the two prior remediation tasks this session) were not independently re-exercised here since this diff touches only `wagle/service.py` and adds one new backend test file — no shared code path with those routes.

## DB Safety

Isolated QA DB (`mc_wagle_qa_db`, port 15446) used for the initial function/HTTP-level reproduction and fully removed after. Isolated `mc_phase2_qa_db` (port 15435, matching `tests/conftest.py`'s own default DSN) used for pytest, fully removed after (`docker rm -f`). Live shared stack (`mongle-db-1`): one additive `membership_role_assignments` row created (`id=13`, membership 4 ← `room_admin`) for the live curl + Playwright smoke, deleted immediately after — final state confirmed identical to the pre-check baseline (`Synthetic Owner A` → `room_admin`, `Synthetic Service Participant` → `participant`, 2 rows, unchanged). No DB reset/drop, no migration, no existing role/permission relationship touched.

## Validation

| Check | Result |
|---|---|
| Reproduction (function + HTTP level) | `MultipleResultsFound`, confirmed twice, before any fix |
| A/B (fix reverted, same 2 tests re-run) | both fail with the identical exception; restored fix → both pass again |
| New pytest (6 cases) | 6/6 PASS |
| Full backend pytest | 411/411 PASS |
| Live curl (`mongle-backend-1`, real login, real dual-role DB row) | 200 |
| Live Playwright (`/wagle`, real login, disposable spec) | PASS, no 500 |
| `git diff --check` | exit 0 |
| `check_all.py` | 0 new warnings |

## Documents

- Created: this handoff, `agent-system/qa/MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001.md`
- Updated (append-only): `agent-system/active.md`, `agent-system/relay/current.md`, `agent-system/qa/COVERAGE_MAP.md`

## Remaining Risks

- No pytest exists yet exercising the SEND/CREATE/MANAGE_ROOM/MANAGE_PARTICIPANTS permission codes under the same 2-role-duplicate shape — those all route through `family_service.effective_permissions`, which is already row-set-based (`.all()` into a `Set[str]`) and structurally cannot exhibit this exact bug, but no dedicated regression test names that guarantee explicitly.
- Product code (`backend/app/domains/wagle/service.py`) and the new test file sit **uncommitted** in `dev-newmarkp`'s real working tree — no commit/push performed per this task's own constraints; PM/Independent-QA action needed to land it.

## Declaration

```
DEVELOPER_SELF_CHECK_COMPLETE
READY_FOR_FOCUSED_INDEPENDENT_QA
```

Next Task: `MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-FOCUSED-INDEPENDENT-QA-001`
