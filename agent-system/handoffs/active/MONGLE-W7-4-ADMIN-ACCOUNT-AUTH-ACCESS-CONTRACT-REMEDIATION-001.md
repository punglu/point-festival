# Handoff — MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001

- Task ID: MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001
- Role: Developer Agent, focused remediation. Full narrative, authority
  table, reproduction evidence, scenario-by-scenario results, security
  checks, and validation run: see this task's own QA evidence file,
  `agent-system/qa/MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001.md`.
  This handoff is a summary pointer only.

## What this task did

Fixed exactly 2 defects raised by
`MONGLE-W7-4-CROSS-DOMAIN-PRODUCT-INTEGRATION-INDEPENDENT-QA-001`:

- **DEFECT-001**: a real Account-native Admin (an `accounts` row linked,
  via the existing `LegacyIdentityMapping` bridge, to a real `admin_auth`
  identity) could not reach `/admin` at all — `AdminProtectedRoute` only
  ever consulted the legacy `isAdmin` flag, which `accountLogin()` always
  sets `false`. Fixed by widening the backend's Admin-authority check
  (`require_admin`, and a second, independently-duplicated guard
  `get_current_admin` discovered mid-task that is the guard `/api/admin/*`
  actually uses) to also accept a linked Account-native token, exposing
  the result via a new additive `AccountContextResponse.is_admin` field,
  and having `AdminProtectedRoute` consult it (with a real loading state,
  no admin-content flash).
- **DEFECT-002**: a legacy Admin JWT with a null `player_id` (the normal
  shape for a pure administrative account) crashed `/api/account-context`
  with a 401, because `_legacy_identity` tested key *presence* rather than
  a non-null value. Fixed by reordering the branch so `role=="admin"` is
  checked first.
- **New defect surfaced only once DEFECT-001's fix made `/admin`
  reachable**: `AdminDashboard`'s `MobileHeader` unconditionally polls
  `/api/chat/unread` (legacy-only), and the app's global 401-interceptor
  read that 401 as session-expired, force-logging-out an
  otherwise-correctly-authorized session. Fixed using the app's own
  existing precedent (`OPTIONAL_ACCOUNT_ENDPOINTS` in `httpClient.ts`,
  already used for `/api/me/wagle/`) — a 1-line addition, no new
  mechanism.

All 5 required scenarios (Account-native Admin linked / legacy Admin
valid-player / legacy Admin null-player / authenticated non-Admin /
unauthenticated) verified via real UI-driven login, including deep-link,
session-restore-on-reload, logout, 3-viewport, and cross-domain regression
smoke. Full detail and exact commands/results in the QA evidence file.

## New finding, not fixed (out of scope)

`GET /api/daily-points/range` 403s for every Admin session (legacy or
Account-native alike) because it requires `role=="player"` literally —
confirmed pre-existing, identical before and after this task's changes,
unrelated to DEFECT-001/002. Leaves the Admin dashboard's weekly
point-chart widget empty; does not block access or cause logout. Tracked
as `API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-PLAYER-ONLY-GAP-001` in
the Coverage Map. Recommends a dedicated follow-up task.

## Explicitly out of scope, untouched

DEFECT-003 (Wagle), Auth/Family/Markpoint policy blockers, W7.6, any RBAC
policy change, any new Admin role, any DB schema/migration change, the
legacy `/api/admin/*` business-logic layer itself, deep-link-return-after-
login (checked and found absent for *every* protected route in the app,
not just Admin — a systemic pre-existing gap, not introduced now).

## Environment note

Backend pytest suite is BLOCKED in this WSL session — no Docker installed,
the isolated test DB (`docker-compose.phase2.yml`, port 15435) required by
`tests/conftest.py` is unreachable. Pre-existing, unrelated to this task.
Substituted with extensive live-curl verification against the running dev
backend, documented in full in the QA evidence file.

## Verdict

`DEVELOPER_SELF_CHECK_COMPLETE` / `FOCUSED_RUNTIME_VERIFICATION_COMPLETE`
/ `READY_FOR_FOCUSED_INDEPENDENT_QA`. Per Invariant 6, NOT self-declared
as `INDEPENDENT_QA_PASS`, `W7_4_CLOSED`, or `W7_6_READY`.

## Closeout Synchronization (Closeout Contract v1)

- ACTIVE: UPDATED
- HANDOFF: UPDATED
- QA EVIDENCE: UPDATED
- COVERAGE MAP: UPDATED
- CLOSEOUT GATE: PASS
- CLOSEOUT GATE Note: documentation-synchronization gate only — the
  substantive verdict is `DEVELOPER_SELF_CHECK_COMPLETE`, explicitly not
  Independent QA PASS; see Verdict above.
- HANDOFF Path: agent-system/handoffs/active/MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001.md
- QA Evidence Path: agent-system/qa/MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-REMEDIATION-001.md

## Next Action

1. A genuinely independent (separate session) QA pass should re-verify
   this fix — recommend opening
   `MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-FOCUSED-INDEPENDENT-QA-001`.
2. `API-W7-4-ADMIN-DASHBOARD-DAILY-POINTS-RANGE-PLAYER-ONLY-GAP-001` (this
   task's own new finding) needs a dedicated follow-up task.
3. DEFECT-003 (Wagle) remains open, out of this task's scope.
4. W7.6 should not start until this task's own Independent QA lands and
   the DEFECT-003/Auth/Family/Markpoint policy-blocker list is reviewed.
