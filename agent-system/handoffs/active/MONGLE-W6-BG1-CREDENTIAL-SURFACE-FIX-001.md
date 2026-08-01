# MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001

- Task ID: MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001
- Kind: backend fix + regression tests — registers and hardens the
  credential-surface change that closes backend gap "BG-1"
  (`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`'s `BLOCKED` finding: no
  single credential reached both the family-context/Wagle API and the
  Markpoint Target API)
- author/agent: `Claude Code`
- created_at: 2026-08-01
- environment: disposable, volume-less PostgreSQL 16.9 container on
  `127.0.0.1:15435` (`mc_phase2`/`mc_festival_phase2`, matching
  `tests/conftest.py`'s expected fixture DB); `database/init.sql` baseline +
  `alembic upgrade head` to `0011`; Python 3.11 venv (system default was 3.9,
  incompatible with this codebase's `X | None` type syntax)

## What was found at task start

`backend/app/dependencies.py` and `backend/app/domains/family/service.py`
were already modified in the working tree (uncommitted, unregistered, no
owning Task ID) to accept an Account-native token on the legacy-shaped
`get_current_user` dependency: the accepted role set widened from
`{player, admin}` to `{player, admin, account}`, and
`resolve_current_account` gained a branch resolving Account tokens via
Session lookup. A docstring attributed the change to
`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`, but that task's own
registration explicitly disclaims backend changes ("No backend product code
was modified"), so the change had no real owner.

Live re-measurement against a fresh disposable DB and real HTTP calls
confirmed the fix works: `/api/account-context` now returns 200 for an
Account token (previously 401 per `BLOCKER_MEASUREMENT.md`), and Wagle's
`/api/families/{id}/wagle/room-summaries` now clears authentication (403
resource-level, not 401).

## The root-cause defect in the as-found fix, and what changed here

The as-found fix's own docstring admitted duplication: `resolve_current_account`'s
new Account branch re-implemented, line for line, the exact same
Session-liveness / sub-vs-session-agreement / Account-active check that
`family.dependencies.get_current_account` (the Wave 1 "Target replacement"
dependency, see its own module docstring) already had. Two independent
copies of a security-critical identity check is a drift risk: a future
Session/Account security fix applied to one copy and not the other would
silently reintroduce a vulnerability.

Fixed by extracting the shared logic into one function,
`auth_service.resolve_account_from_session_claim(db, payload)`
(`backend/app/domains/family/auth_service.py`), and having both call sites
use it:

- `family/dependencies.py::get_current_account` — now decodes the token and
  delegates.
- `family/service.py::resolve_current_account` — Account branch now
  delegates the same way.

No behavior changed; this is a pure extract-shared-function refactor,
confirmed by full regression (see below).

## Safety review performed (the actual re-verification requested)

Enumerated every one of the 38 `Depends(get_current_user)` usages across 8
files reachable from `app/dependencies.py`'s widened role set (not just
Wagle) to check for an unsafe direct `user["sub"]` extraction that could
treat an Account token's `sub` (an `account_id`) as a legacy `player_id`:

- `family/router.py`, `wagle/router.py` (all 15 handlers) — every one
  resolves identity exclusively through `resolve_current_account` /
  `service.require_permission` / `wagle.service.context()`, never a raw
  `user["sub"]` read.
- `feedback/router.py` — the only file with a direct `int(user["sub"])`
  read, but it sits behind an explicit `role in {"player", "admin"}` gate
  that rejects an `account`-role token with 403 before that line is ever
  reached.
- `config/cheer/auth` routers — take `user` as an unused `_: dict`; identity
  is never extracted, so the widened role set has no effect there beyond
  "some valid token is required."
- `chat/admin/mission_template` routers use a completely separate
  `app.domains.auth.dependencies.get_current_user` — untouched by this
  change.

No identity-confusion / IDOR-class defect found. Confirmed with a
worst-case regression test: an Account and a legacy Player sharing the same
numeric id (both are row 1 of a freshly truncated table) still cannot be
confused, because the role gate rejects the Account token before any `sub`
value is ever compared to that player's data.

## Verification

- Fresh migration `0000` → `0011` on a brand-new disposable container:
  clean.
- `tests/test_account_auth_wave1.py`: 33/33 pass (no regression to Wave 1
  Account auth).
- `tests/test_wagle_realtime_wave3.py` + family/account-scoped tests: 41/41
  pass.
- New file `backend/tests/test_bg1_credential_surface_unification.py`, 5
  tests, all pass: Account token reaches `/api/account-context` (the fix
  itself); a revoked Session is rejected identically by both entry points
  (`/api/me` via `get_current_account`, `/api/account-context` via
  `get_current_user`+`resolve_current_account`) — this is the specific
  property the refactor guarantees and the as-found duplicated version did
  not; a suspended Account is rejected (403) via the legacy-shaped entry
  point too; the widened role set does not bypass a route that explicitly
  requires `player`/`admin` (403); the id-collision worst case above.
- Full `backend/tests/` suite: 317 passed, 0 failed, 0 errors (re-run twice;
  an earlier combined run showed 3 failed/11 errors that reproduced as
  pre-existing cross-file batch flakiness unrelated to this change — the
  same failing files pass 86/86 when run standalone).
- Disposable DB container and throwaway Python venv torn down after use;
  zero residue.

## Changed files

- `backend/app/dependencies.py` (already present, unregistered — role set
  widened to `{player, admin, account}`, docstring)
- `backend/app/domains/family/service.py` (already present, unregistered —
  `resolve_current_account` Account branch; now delegates to the shared
  function instead of duplicating it)
- `backend/app/domains/family/dependencies.py` (this task — `get_current_account`
  now delegates to the shared function)
- `backend/app/domains/family/auth_service.py` (this task — new
  `resolve_account_from_session_claim`)
- `backend/tests/test_bg1_credential_surface_unification.py` (this task —
  new, 5 tests)

## Risks and Human Gate

- This is an authentication-boundary change. It is backed by regression
  tests and a full-suite re-run, but has not gone through independent QA by
  a separate session, which the repository's own convention treats as
  mandatory for security/DB/auth boundary work.
- No frontend, migration, or deployment config was touched.

## Next agent first action

Independent QA of this task's specific claims (the shared-function
refactor, the 38-usage safety enumeration, the 5 new tests, the full-suite
317/0/0 result) before this is treated as closing BG-1 for Wave 6 Target UI
purposes.

## Forbidden Scope (as declared by this task)

Frontend code, any other backend domain not touched above, migrations,
deployment config, resolving Wagle's remaining resource-level 403 on
`room-summaries` (needs Wagle participant/subscription seed data, not a
credential-surface issue).

## Closeout Synchronization

- Closeout Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001.md`
- Independent QA: `not started`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: added `API-W6-BG1-CREDENTIAL-SURFACE-001` for `test_bg1_credential_surface_unification.py`; `PARTIAL`/`NOT_CONFIRMED` pending independent QA.
- CLOSEOUT GATE: `BLOCKED`
- CLOSEOUT GATE Reason: fix implemented, root-cause duplication removed, regression-tested and full-suite verified; independent QA still pending, so the gate cannot read PASS yet.
