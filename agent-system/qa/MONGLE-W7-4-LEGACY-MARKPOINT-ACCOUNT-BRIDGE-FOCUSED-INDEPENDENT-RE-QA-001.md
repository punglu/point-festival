# QA Evidence — MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001

- Task ID: `MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001`
- author/agent: independent QA session (fresh session; no prior involvement in the legacy
  Markpoint account-bridge remediation or either of the two prior remediations still uncommitted
  in this worktree). Runtime/browser execution (Sections 5–14 below) was carried out by a
  delegated sub-session under this session's direct instruction and specification, and its
  cleanup claims were independently re-verified by this session before this report was written
  (see "Independent re-verification of cleanup" below).
- observed_at: 2026-08-07
- git_ref: `5ba398c` (branch `dev-newmarkp`) — plus an **uncommitted** working-tree diff, unchanged
  in shape from before this session started: 10 modified files (`agent-system/active.md`,
  `agent-system/relay/current.md`, `backend/app/domains/markpoint_target/router.py`,
  `frontend/src/App.tsx`, `frontend/src/platform/access/AccessBoundary.tsx`,
  `frontend/src/platform/pages/FamilyLanding.tsx`, `frontend/src/shared/api/httpClient.ts`,
  `frontend/src/shared/family/FamilyContextLoader.tsx`, `tests/e2e/specs-mongle/01-shell.spec.ts`,
  `tests/e2e/specs-mongle/03-target-ui.spec.ts`) and 5 untracked files (this task's own new
  backend test plus 4 pre-existing QA/handoff docs for two other task IDs). Only
  `backend/app/domains/markpoint_target/router.py` and
  `backend/tests/test_markpoint_legacy_account_bridge_wave7.py` (new) are this task's own scope;
  the rest are the two prior, separately-QA'd remediations
  (`MONGLE-W7-4-MARKPOINT-ADMIN-ROUTE-AND-LEGACY-NOTIFICATION-SESSION-REMEDIATION-001` and
  `MONGLE-W7-4-MULTI-FAMILY-ACTIVEFAMILY-PERSISTENCE-REMEDIATION-001`), only re-checked here as
  regression smoke per this task's own Section 10.
- environment: WSL (Linux), no Docker in this session (confirmed: `docker info` fails). Native
  stack: the local Postgres cluster already running at `127.0.0.1:5432`
  (`mc_admin`/`mc_local_dev_2026`, confirmed with a real `select 1` query before use) and
  `backend/.venv` as the Python interpreter. Backend run via a throwaway `uvicorn app.main:app`,
  frontend via a throwaway `vite` dev server, following the repository's own documented
  native-launcher pattern (`tests/e2e/scripts/run-w75-full-spec-native.sh`, read in full before
  building a disposable scratch equivalent). Disposable databases used the naming
  `mc_w74_indqa_r7x9*`; the pre-existing, unexplained `mc_qa_markpoint_reqa_001` on the same
  cluster was never read, written, or dropped by either the delegated sub-session or this session.
- evidence: this file + the Session Handoff at `agent-system/handoffs/active/
  MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001.md`
- secrets_redacted: `true`
- Verdict: PASS
- Closeout Contract: `v1`
- Independent from implementer: `true`
- Independent QA: `complete`

## Independent QA qualification

- Separate fresh session: YES
- Prior remediation involvement: NO
- Product/test read-only: YES — this session's own `Edit`/`Write` calls never targeted
  `frontend/src/**` or `backend/app/**` or any committed test file. The delegated sub-session's
  writes were confirmed (by this session, independently) to be limited to disposable scratch
  files under `tests/e2e/.runtime/w74-indqa/` and `tests/e2e/test-results/`, all deleted before
  this report — see "Independent re-verification of cleanup" below.
- Finding-only handling: YES — all items in Findings/Next Action are reported, not fixed.
- **Independent QA Qualification: PASS**

## Start Gate (baseline)

`pwd` → `/appl/point-festival`; `git rev-parse --show-toplevel` → same; `git branch --show-current`
→ `dev-newmarkp`; `git rev-parse HEAD` → `5ba398c2750dbbb172c66496a92998d5efb0ad98`; `git status
--short` → the 10 modified + 5 untracked files listed above; `git diff --stat`/`--name-status`
matched; `git diff --check` → clean (exit 0); `git stash list` → empty; `git log -12 --oneline`
matched the PM-supplied candidates; `git remote -v` → `origin` = `https://github.com/punglu/
point-festival`; `git fetch --prune` → no new refs; `git rev-parse HEAD` and `git rev-parse
'@{u}'` identical (no divergence, no detached HEAD, no unresolved merge/rebase).

Dirty/untracked classification (all read directly, not inferred): `backend/app/domains/
markpoint_target/router.py` and `backend/tests/test_markpoint_legacy_account_bridge_wave7.py` →
**D. THIS TASK'S OWN REMEDIATION**. `frontend/src/App.tsx`, `frontend/src/platform/access/
AccessBoundary.tsx`, `frontend/src/platform/pages/FamilyLanding.tsx`, `frontend/src/shared/api/
httpClient.ts`, `frontend/src/shared/family/FamilyContextLoader.tsx`,
`tests/e2e/specs-mongle/01-shell.spec.ts`, `tests/e2e/specs-mongle/03-target-ui.spec.ts` →
**A/B. PRIOR REMEDIATIONS** (Markpoint-admin-route/notification and ActiveFamily-persistence,
both already independently QA'd — Admin PASS, ActiveFamily PASS, Notification/Cross-domain FAIL
pending exactly this task's fix). `agent-system/active.md`, `agent-system/relay/current.md` →
**C. PRIOR QA/REMEDIATION TRACKING** (append-only entries for the two tasks above, read in full,
content matches their own stated scope, not a blocker). The 4 pre-existing untracked QA/handoff
docs → **C**, different task IDs from this one, not touched. No `F`/`G` (OTHER_TASK/UNKNOWN)
files found. No `reset`/`clean`/`restore`/`stash`/`merge`/`rebase`/`commit`/`push` was ever run by
this session or the delegated sub-session.

**Governance deviation check**: the Developer report for the remediation task disclosed one
`git stash` of only `router.py` during baseline reproduction, popped immediately. `git stash list`
was empty at this session's Start Gate and remained empty throughout (re-checked after the
delegated sub-session's work). The final `router.py` diff matches the remediation's own
in-code description and commit-adjacent handoff exactly (see Verified Diff Gate below) — no
integrity gap found. `GOVERNANCE_DEVIATION_INTEGRITY_UNVERIFIABLE` does not apply.

## Verified Diff Gate

Read directly via `git diff`, not summarized from any report.

**`router.py`** (this task's own scope): the private `_me` dependency shared by all
`/api/me/markpoint/*` GET routes changed from `account: Account = Depends(get_current_account)`
(strict, Account-native-only resolver in `family/dependencies.py`) to
`user: dict = Depends(get_current_user)` followed by
`account = await family_service.resolve_current_account(db, user)` — the same legacy-bridge-aware
pair `/api/account-context` already uses. The subsequent
`family_service.get_active_membership(db, account.id, family_id)` call is unchanged. Confirmed via
`git diff --stat` on `backend/app/domains/family/dependencies.py`, `backend/app/domains/family/
service.py`, `backend/app/domains/markpoint_target/service.py`, `backend/app/domains/
markpoint_target/schemas.py`, `backend/app/dependencies.py`, and every file under
`backend/app/domains/wagle`: **zero diff on all of them** — `get_current_account` itself,
`get_family_membership`, response schemas, calculation logic, and the Wagle domain are all
untouched. No new identity-bridge implementation was introduced; the existing
`resolve_current_account` is reused as-is.

**New test file** (`backend/tests/test_markpoint_legacy_account_bridge_wave7.py`, untracked, this
task's own): real `client`/`db` fixtures issuing real HTTP requests (not service-level mocks),
covering all 9 GET paths for both a legacy-bridged actor and an Account-native actor, an
identity-parity check, mapping-missing, mapping-not-linked, no-membership, cross-family,
inactive-subscription, no-token, forged-token, and two blast-radius guards (admin-route and
Wagle-realtime dependencies still reject a legacy token). Grep confirmed no `.only`/`.skip`
anywhere in this file or in the two prior remediations' test diffs. No existing assertion in
`01-shell.spec.ts` or `03-target-ui.spec.ts` was deleted or weakened — both diffs are strictly
additive.

**Frontend, re-checked for this task's own concern**: `httpClient.ts`'s
`OPTIONAL_ACCOUNT_ENDPOINTS` array gained only `/api/me/notifications` (prior task); **no**
`/api/me/markpoint/*` path was added to it, and no other interceptor logic changed. This matters
directly for this task: the legacy-bridge fix has to make Markpoint's backend genuinely return
200, not have the frontend mask a 401 — confirmed that is exactly what happened (see Axis A/B).

No `POST_REMEDIATION_DIFF_MISMATCH` found: the actual diff matches the reported remediation.

## Runtime and Fixture

No Docker in this WSL session (confirmed). The delegated sub-session read
`tests/e2e/scripts/run-w75-full-spec-native.sh` in full and built a new, disposable scratch
launcher and Playwright config under `tests/e2e/.runtime/w74-indqa/` (deleted at cleanup, never
committed) targeting the actual spec files under test rather than the committed script's single
hardcoded spec, and defining the three required non-desktop viewport projects. Fixture: a
disposable, migrated (`init.sql` → `alembic upgrade head`), seeded database
(`mc_w74_indqa_r7x9`) with the required actor set — a legacy-PIN player bridged via
`LegacyIdentityMapping` to a canonical Account with an active Family membership and Markpoint
role, a comparison Account-native peer in the same family, a second family for cross-family
checks, an unmapped legacy player, a mapped-but-`candidate`-status legacy actor, a member with no
Markpoint subscription, and (ad hoc, beyond the minimum) a soft-deleted/revoked legacy identity
case. Each family carried its own identifiable Markpoint mission data.

## Endpoint Inventory

Enumerated directly from `backend/app/domains/markpoint_target/router.py`'s current source (not
assumed from any report): all 9 `GET /api/me/markpoint/*` routes share the one fixed `_me`
dependency —

| Path | Family scope | Access gate |
|---|---|---|
| `missions` | `family_id` query param, resolved via `_me` → `get_active_membership` | membership + subscription check inside `get_active_membership`/service layer |
| `ledger` | same | same |
| `balance` | same | same |
| `level` | same | same |
| `summary` | same | same |
| `deductions` | same | same |
| `weekly` | same | same |
| `projection` | same | same |
| `deductions/history` | same | same |

No 10th route was found; the previously-reported figure of 9 is confirmed accurate against
current source.

## Axis A — Legacy Markpoint Bridge (real HTTP against a live throwaway backend)

All checks performed via direct `curl`/HTTP against the disposable-DB-backed backend, independent
of the new pytest file:

- **A1** — all 9 endpoints: **200** for the legacy-bridged token, correct family-scoped data.
- **A2** — Account-native regression: all 9 endpoints **200**, unchanged shape/scope.
- **A3** — no `LegacyIdentityMapping`: **403**, `"계정 매핑이 필요합니다"`.
- **A3b** — mapping present but `mapping_status="candidate"` (not `linked`): **403**, same message
  — not treated as authorization, matching the bridge's existing contract elsewhere.
- **A4** — mapped Account, no membership in the target family: **403**,
  `"활성 가족 구성원 권한이 필요합니다"`.
- **A5** — valid membership, inactive Markpoint subscription: **403**,
  `"Markpoint 접근 권한이 없습니다"`.
- **A6** — cross-family: **403**, zero leakage (the same-family case above already proves 200 with
  real data, so this 403 is a genuine denial, not an unrelated empty result).
- **A7** — no token: **401**.
- **A8** — forged token: **401**.
- **A9** — soft-deleted/revoked legacy identity (beyond the minimum, current models permit it): the
  still-valid existing session token → **403**, `"활성 레거시 인증이 필요합니다"`; a fresh
  re-login attempt → **404**. Identity was restored afterward and re-verified working, leaving no
  residual fixture damage.
- **Blast-radius guards**: `GET /api/families/{id}/markpoint/templates` (uses
  `get_family_membership`, untouched) still **401**s a legacy token; `GET /api/me/wagle/
  realtime-context` (uses `get_current_account`, untouched, Wagle's own deliberate
  legacy-exclusive boundary) still **401**s a legacy token.
- **Identity parity**: a legacy-bridged login and a native login for the *same* seeded person
  returned byte-identical real mission data — the bridge resolves to the same canonical Account,
  not a divergent or fabricated identity.

**Axis A verdict: PASS.**

## Axis B — Notification Session Continuity (real, unmocked browser)

Real Chromium (Playwright 1.58.2, pinned) against the live throwaway backend+frontend:

- **B1**: legacy-PIN login → family selected → `GET /api/me/notifications` real 401 observed →
  session/token intact (`sessionStorage.accessToken` present, no `mc_session_expired`) → no forced
  redirect → real navigation to `/markpoint` → all Markpoint core API calls 200 → real DOM
  (`마크포인트` heading, actual data) rendered.
- **B2**: a genuine 401 on an ordinary protected endpoint (not `/api/me/notifications`) → session
  cleared, redirected — verified through the real interceptor code path. The committed test's
  known `page.reload()`-timing race (already documented by the prior QA lineage as a
  test-construction fragility, not a product defect) was worked around in the scratch spec with
  `waitUntil:'commit'` rather than depending on `reload()`'s own navigation promise; the underlying
  product contract holds either way.
- **B3**: Account-native login → `/api/me/notifications` 200 → session intact → Markpoint normal.

**Axis B verdict: PASS.**

## Axis C — Cross-Domain Legacy Flow (single continuous real browser session)

legacy-PIN login → family select → Family Home → notification 401 (session survives) → real
navigation to `/markpoint` → real core content renders → reload (family/session preserved) →
browser back/forward (state preserved) → logout. Completed end to end at viewport `1180×820`
(full 7/7 scratch-spec run: sanity, B1, B2, B3, full Axis-C flow, Admin smoke, ActiveFamily
smoke), and B1 + the full Axis-C flow independently re-confirmed green at `390×844` and
`820×1180`, including an added `scrollWidth − clientWidth ≤ 1` horizontal-overflow check at all
three. No cross-family data observed leaking into any of these flows.

**Axis C verdict: PASS.**

## Prior-PASS Regression Smoke

- **Markpoint Admin**: smoke-level owner/admin real content access, member/unauthenticated
  denial — clean, no regression, included in the 7/7 scratch run above.
- **ActiveFamily**: smoke-level multi-family select → reload → `/markpoint` navigation, family
  choice preserved — clean, no regression, included in the same run.

**Prior-PASS Regression verdict: PASS.**

## Viewports

All three required viewports exercised for B1/Axis-C: `390×844`, `820×1180`, `1180×820`. Legacy
login, family selector, Markpoint core content render, loading completion, no forced redirect, no
horizontal overflow, and no error fallback confirmed at each.

## Test Execution

1. **New focused backend test** (`test_markpoint_legacy_account_bridge_wave7.py`): run to
   completion twice, **28/28 passed** both times.
2. **Related targeted backend files run individually** (`test_account_auth_wave1.py`,
   `test_auth_admin_login.py`, `test_integration_wagle_markpoint.py`,
   `test_markpoint_access_wave4.py`, `test_markpoint_core_gap_wave5.py`,
   `test_markpoint_http_authorization_wave5.py`, `test_markpoint_target_wave5.py`,
   `test_bg1_credential_surface_unification.py`, `test_wagle_permission_role_cardinality.py`):
   **NOT independently confirmed as a standalone per-file run** — this specific invocation was
   interrupted (by this session's own stop-and-cleanup order, issued after two ambiguous
   mid-run status reports from the delegated sub-session) before it printed a final summary line.
   This is reported honestly as incomplete rather than backfilled as PASS. It does **not** reduce
   confidence in the underlying contract, because every one of these files is included in, and
   passed as part of, the full-suite run immediately below, which did run to completion.
3. **Full backend suite** (`cd backend && python3 -m pytest -q`, `backend/.venv` interpreter):
   ran to full completion (~12m37s), **439 passed, 0 failed**.
4. **Frontend**: `pnpm run lint` — clean. `pnpm run build` (`tsc -b && vite build`, which covers
   typecheck) — clean, zero type errors, only the pre-existing >500kB chunk-size advisory
   (not new).
5. **Static**: `git diff --check` — clean (exit 0). `python3 agent-system/tools/check_all.py` —
   ran, report-only; every warning present is pre-existing and attributable to other task IDs;
   none new from this task's own diff.

## Test Integrity

Neither this session nor the delegated sub-session modified `tests/e2e/specs-mongle/
01-shell.spec.ts` or `03-target-ui.spec.ts`, weakened any assertion, or added `.skip`/`.only` to
any committed file. Two pre-existing, already-documented test-maintenance items (not fixed, per
policy):
- `01-shell.spec.ts`'s `loginAsFirstPlayer()` helper's stale locator, worked around with a
  disposable scratch spec using the current, correct selector — classified `STALE_TEST`.
- The "genuine protected-endpoint 401" test's `page.reload()`-based timing race, worked around in
  the scratch spec with a non-reload-dependent recheck — classified `TEST_CONSTRUCTION_DEFECT`.

## Independent re-verification of cleanup

Before writing this report, this session independently re-ran the checks the delegated
sub-session claimed, rather than accepting its self-report at face value:
`git status --short` → confirmed identical to the pre-session baseline (10 modified + 5
untracked, nothing added or missing); `ps aux | grep -E "uvicorn|vite|playwright|chromium"` →
only one pre-existing `vite --port 5299` process remained, confirmed to predate this session and
not started by it — left untouched; `select datname from pg_database where datname like
'mc_w74%'` → zero rows, all disposable databases dropped; `mc_qa_markpoint_reqa_001` confirmed
still present and untouched; `ls tests/e2e/.runtime/` → only pre-existing sibling directories from
other tasks remained, the sub-session's own `w74-indqa/` directory and `tests/e2e/test-results/`
were both gone; `git stash list` → empty.

## Changes

Zero product-code changes. Zero test-file changes. This file, its paired Handoff, and the
append-only entries to `agent-system/active.md`/`agent-system/relay/current.md` are the only
material this session leaves behind in the real repository. Zero commits, zero pushes.

## Axis verdicts

| Axis | Verdict |
|---|---|
| Legacy Markpoint Bridge | **PASS** |
| Notification Session | **PASS** |
| Cross-domain | **PASS** |
| Prior-PASS Regression (Admin/ActiveFamily) | **PASS** |

## Overall verdict: PASS

All four axes PASS with real, unmocked evidence (backend HTTP for Axis A; real Chromium browser
runs across all 3 required viewports for Axis B/C and the regression smoke). The full backend
suite passed in full (439/439), frontend lint/build are clean, static checks are clean, and
cleanup was independently re-verified by this session rather than only trusted from the delegated
sub-session's own report. The one incomplete item (per-file breakdown of the "related targeted
backend" group) is disclosed above as `NOT RUN` standalone rather than folded into the PASS
silently; it does not gate Overall PASS because the same files are proven by the completed
full-suite run.

## Findings (finding-only — none fixed by this session)

1. **Minor, non-blocking**: `tests/README.md` still documents the frontend package manager as
   `npm`; the frontend migrated to `pnpm` (`frontend/package.json`:
   `"packageManager": "pnpm@10.32.1"`, `frontend/pnpm-lock.yaml` present, no
   `package-lock.json`) per commit `0319940`. Documentation drift, not a product defect — a
   future doc-maintenance task should update `tests/README.md`'s frontend command examples.
2. Carried forward, not newly introduced by this task: `01-shell.spec.ts`'s
   `loginAsFirstPlayer()` stale locator and the reload-based timing race in the genuine-401 test
   (see Test Integrity above) — both pre-existing test-maintenance items outside this task's
   scope to fix.

## Next action

1. This task's fix and the two prior remediations it depends on (`...ADMIN-ROUTE-AND-LEGACY-
   NOTIFICATION-SESSION-REMEDIATION-001`, `...MULTI-FAMILY-ACTIVEFAMILY-PERSISTENCE-
   REMEDIATION-001`) are now all independently PASS-verified. This 10-modified/5-untracked diff
   is ready for a Branch Integration task to commit as a bundle, subject to PM commit-scope
   review (per this repo's own commit-scope discipline).
2. `01-shell.spec.ts`'s `loginAsFirstPlayer()` locator and the reload-based timing race in its
   genuine-401 test remain open, separate test-maintenance items (not blocking this task's PASS).
3. `tests/README.md`'s frontend command section should be updated from `npm` to `pnpm` in a future
   documentation task.
4. PM should confirm the origin of `mc_qa_markpoint_reqa_001` on the shared native Postgres
   cluster — still unexplained across three consecutive independent QA sessions that have each
   observed it and left it untouched.
