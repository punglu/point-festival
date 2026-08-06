# QA Evidence — MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001

- Task ID: `MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001`
- author/agent: independent QA session (fresh session; no prior involvement in the
  Markpoint-admin-route, notification-session, or ActiveFamily-persistence remediation)
- observed_at: 2026-08-06/07 (session spanned local midnight)
- git_ref: `5ba398c` (branch `dev-newmarkp`) — the FAIL report commit — plus an **uncommitted**
  working-tree diff (7 files: `frontend/src/App.tsx`, `frontend/src/platform/access/
  AccessBoundary.tsx`, `frontend/src/platform/pages/FamilyLanding.tsx`, `frontend/src/shared/
  api/httpClient.ts`, `frontend/src/shared/family/FamilyContextLoader.tsx`,
  `tests/e2e/specs-mongle/01-shell.spec.ts`, `tests/e2e/specs-mongle/03-target-ui.spec.ts`) that
  is the actual remediation under test. Neither `agent-system/active.md` nor
  `agent-system/relay/current.md` contains any entry past the FAIL report — the remediation was
  never documented before this QA. Two remediation task IDs were recovered from in-code comments
  in the diff itself: `MONGLE-W7-4-MARKPOINT-ADMIN-ROUTE-AND-LEGACY-NOTIFICATION-SESSION-
  REMEDIATION-001` (App.tsx route + httpClient.ts optional-endpoint entries) and
  `MONGLE-W7-4-MULTI-FAMILY-ACTIVEFAMILY-PERSISTENCE-REMEDIATION-001` (AccessBoundary.tsx +
  FamilyLanding.tsx + FamilyContextLoader.tsx). No handoff/QA-evidence document for either
  exists yet.
- environment: WSL (Linux), no Docker in this session (confirmed: `which docker` → nothing).
  Native stack used instead: a local Postgres 16-class cluster already running on
  `127.0.0.1:5432` (`mc_admin` / `mc_local_dev_2026`, confirmed via `pg_isready` + a real
  connection before use) and a pre-provisioned `backend/.venv`. Backend run via
  `uvicorn app.main:app`, frontend served natively via `./node_modules/.bin/vite`
  (`VITE_DEV_PROXY_TARGET` pointed at the disposable backend port), matching the repo's own
  documented native-launcher pattern (`tests/e2e/scripts/run-w75-full-spec-native.sh`). All
  disposable databases used the naming `mc_w74_qa_*`, none touched the pre-existing persistent
  `mongle`-project stack or any other session's database (one unrelated, pre-existing DB —
  `mc_qa_markpoint_reqa_001` — was observed on the same cluster and was never read, written, or
  dropped by this session; flagged in Next Action for PM attention since it does not belong to
  this session and its origin is unknown).
- evidence: this file + the Session Handoff at `agent-system/handoffs/active/
  MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001.md`
- secrets_redacted: `true`
- Verdict: FAIL
- Closeout Contract: `v1`
- Independent from implementer: `true`
- Independent QA: `complete`

## Independent QA qualification

- Separate fresh session: YES
- Prior remediation involvement: NO
- Product/test read-only: YES (zero `Edit`/`Write` call ever targeted `frontend/src/**` or
  `backend/app/**`; the only writes were this session's own disposable scratch Playwright specs/
  configs/launcher script under `tests/e2e/specs-mongle-scratch/` and two scratch top-level
  `tests/e2e/` files, all deleted before this report, plus this evidence/handoff pair)
- Finding-only handling: YES (all defects below are reported, not fixed)
- **Independent QA Qualification: PASS**

## Start Gate (baseline)

`pwd` → `/appl/point-festival`; `git rev-parse --show-toplevel` → same; `git branch --show-current`
→ `dev-newmarkp`; `git rev-parse HEAD` → `5ba398c2750dbbb172c66496a92998d5efb0ad98`; `git status
--short` → the 7 files listed above (all `M`, none untracked); `git diff --stat` / `--name-status`
matched; `git diff --check` → clean (exit 0, before and after); `git stash list` → empty; `git log
-10 --oneline` matched the PM-supplied candidates; `git remote -v` → `origin` =
`https://github.com/punglu/point-festival`; `git fetch --prune` → no new refs, HEAD unchanged,
`@{u}` identical to HEAD (no divergence, no detached HEAD, no unresolved merge/rebase).

Dirty-file classification: all 7 files → **A. MARKPOINT_NOTIFICATION_REMEDIATION** (5 App/
AccessBoundary/FamilyLanding/httpClient/FamilyContextLoader files) or the paired test additions
in the same category, plus **B. ACTIVEFAMILY_REMEDIATION** for the `AccessBoundary.tsx`/
`FamilyLanding.tsx`/`FamilyContextLoader.tsx` trio specifically (their own in-code comments
attribute them to the second task ID) — no `D`/`E` (OTHER_TASK/UNKNOWN) files. No `reset`/
`clean`/`restore`/`stash`/`merge`/`rebase`/`commit`/`push` was ever run.

## Verified Diff Gate

Every one of the 7 files was read via `git diff` directly (not summarized from memory or from
any prior report).

**Markpoint route** (`App.tsx`): adds exactly one `<Route path="/markpoint/admin">`, reusing the
existing `MarkpointAdmin` component (confirmed unchanged — 0 diff on
`frontend/src/platform/markpoint/MarkpointAdmin.tsx`), the existing `ProductContext`, the existing
`ProtectedRoute`, and the existing `MongleAppShell`, with the identical wrapping pattern already
used immediately above it for `/markpoint`. No backend file changed (`git status --short` has zero
`backend/` entries). `MongleAppShell.tsx`'s own nav item (`to: '/markpoint/admin'`, pre-existing,
unchanged) and `MarkpointAdmin.tsx`'s own internal permission gating (unchanged, does not use
`AccessBoundary` — verified via `grep`) were both confirmed still in place, not rewritten.

**Notification 401** (`httpClient.ts`): adds exactly one entry, `/api/me/notifications`, to the
pre-existing `OPTIONAL_ACCOUNT_ENDPOINTS` array (which already held `/api/me/wagle/` and
`/api/chat/unread`). No wildcard/prefix that would swallow all of `/api/me/*` was introduced. The
non-optional 401 branch (session clear + redirect) is untouched.

**ActiveFamily** (`AccessBoundary.tsx` + `FamilyLanding.tsx` + `FamilyContextLoader.tsx`):
`AccessBoundary` gains an `allowFamilySelection` prop, **defaulting to `false`** (verified: the
default parameter is `allowFamilySelection = false`), preserving the existing gate for every
consumer that does not pass it. Confirmed via `grep -rn "AccessBoundary"` across `frontend/src`
that there are exactly two JSX consumers: `FamilyLandingPage` (now passes
`allowFamilySelection`) and `MarkpointUser`'s route wrapper (unchanged, no new prop — still gated).
`FamilyContextLoader.tsx` adds `token` (from `useAuthStore`) to its existing reload `useEffect`'s
dependency array, so an identity switch without an intervening logout (a fresh JWT, `isLoggedIn`
already `true`) now correctly re-triggers `load()`; no storage-key or membership-validation logic
in `useFamilyContextStore.ts` / `activeFamilyStorageMigration.ts` was touched by this diff (both
files have 0 diff — read in full, unrelated to this remediation).

**Test diffs**: `01-shell.spec.ts` adds two new tests (notification-401-survives,
genuine-401-clears) under the Markpoint-admin-route-and-notification task ID.
`03-target-ui.spec.ts` adds a new `Journey 1b — ActiveFamily persistence` describe block (8 cases)
under the ActiveFamily task ID. No existing test in either file was modified, skipped, or weakened
— confirmed by diffing only additive hunks.

No `POST_REMEDIATION_DIFF_MISMATCH` was found: every file's actual change matches its own in-code
description.

## Runtime and Fixture

No Docker in this WSL session (confirmed). The repository's own native-launcher pattern
(`tests/e2e/scripts/run-w75-full-spec-native.sh`) was followed for a **new, disposable, scratch**
launcher script (deleted at cleanup, never committed) rather than modifying the committed one,
because the committed script hardcodes one spec file and this task needed different targets.
Playwright 1.58.2, Chromium already installed under `tests/e2e/node_modules/playwright-core/
.local-browsers`. A scratch Playwright config (deleted at cleanup) defined the three required
viewport projects — `390×844`, `820×1180`, `1180×820` — since the committed
`playwright.mongle-manual.config.ts` only defines one `desktop` project and
`playwright.mongle.config.ts` requires the (unavailable) Docker stack.

Fixture: the repository's own official seed, `backend/scripts/phase1_seed_synthetic.py`, run
against a disposable native Postgres database (`database/init.sql` + `alembic upgrade head`, then
the seed script), same actors used by every prior sibling QA in this lineage: `owner.a`
(Family Alpha + Beta, `mission_manager`), `admin.a` (Family Alpha, `point_admin`), `member.a`
(Family Alpha, plain member), `member.b` (Family Beta only), plus the legacy `players` table from
`database/init.sql` (유빈/유현/아빠/엄마, legacy player 1 bridged to Account `owner.a` via
`LegacyIdentityMapping`). Family Alpha vs Beta gave every cross-family check real, distinguishable
data.

**Environment limitation discovered and worked around**: `tests/e2e/specs-mongle/01-shell.spec.ts`'s
own `loginAsFirstPlayer()` helper uses `page.locator('button[class*="playerCard"]')`, a locator
that does not match any class in the current `ProfileSelectorScreen.tsx` (its real classes are
`styles.profile`/`styles.profileLocked`, confirmed by reading the component — CSS Modules, but the
literal substring `playerCard` appears nowhere in the source). This is **pre-existing and
unrelated to this remediation** (the helper itself is outside every diff hunk in this task). It
blocks essentially every test in `01-shell.spec.ts`, including both of the two new
notification-session tests this remediation added. Because Section 6 of this task's own brief
requires genuine, unmocked browser evidence for the Notification Session axis regardless, this
session wrote a disposable scratch spec (`specs-mongle-scratch/qa-w74-re-axis-ab.spec.ts`, deleted
at cleanup) that re-drives the *same* scenarios with the current, correct selector
(`page.getByRole('button').filter({ hasText: '유빈' })`), asserting nothing the committed spec
doesn't already assert in substance. This is reported as a `STALE_SPEC_FAILURE` for
`01-shell.spec.ts`'s existing 18 non-new tests plus the 2 new ones, not a product defect, and was
never edited.

## Test Execution

Three real, unmocked-flow runs were performed (details in the Handoff). Key results:

1. **Backend targeted pytest** (12 files matching the prior FAIL report's own list, disposable
   native Postgres): **213 passed, 0 failed** — identical to the prior report's own count,
   consistent with a genuinely zero backend diff.
2. **Frontend static**: `pnpm run lint` clean; `pnpm run build` (`tsc -b && vite build`) clean,
   668 modules, only the pre-existing >500kB chunk advisory (not new).
3. **Serialized Playwright run** (`--workers=1`, to eliminate cross-project data races against the
   one shared native backend — see below), `03-target-ui.spec.ts` + the scratch Axis A/B spec,
   3 viewport projects: **69 passed / 33 failed** of 102. Failure classification:
   - **5 pre-existing, out-of-scope, `STALE_SPEC_FAILURE` or `ENVIRONMENT_REQUIRED`** per
     viewport, unchanged from the original FAIL report and *not* part of this remediation's
     scope: Journey 2's first test (`getByRole('heading',{name:'마크포인트'})` — the real,
     current, intentional heading is `포인트 잔치`, already disclosed in the FAIL report as
     `SPEC_STALE`) and Journey 4/6's Wagle-realtime tests (native Vite dev proxy does not set
     `ws: true`, already disclosed as `ENVIRONMENT_REQUIRED`).
   - **A number of Journey 2/3 tests failed only on the 2nd/3rd viewport project** (tablet/
     desktop), not on the 1st (mobile). Root-caused to this session's own scratch harness running
     the *same* mutating spec three times against *one* persistent, un-reseeded backend (a mission
     approved/materialized by the mobile run is no longer in its original state for the tablet/
     desktop runs) — an `ENVIRONMENT_FAILURE`/`FIXTURE_FAILURE` of this ad hoc 3-viewport
     harness, not a product defect. Confirmed by the fact that every one of these tests passed
     cleanly on the first (freshest-data) project.
   - **Journey 1b (ActiveFamily persistence, all 8 cases) passed at all 3 viewports with zero
     failures** — the cleanest, most direct evidence for Axis C.
   - **Two of this session's own scratch-test assertions were themselves flawed** (not product
     defects): "cross-family: Family Beta data never leaks" failed because `owner.a`'s legitimate
     multi-family header switcher naturally lists both family names it belongs to — the actual
     admin *content* (mission table) showed only Family Alpha's own rows in every failure
     snapshot, zero real leakage. A handful of other scratch-test failures (nav/CTA click, reload
     preservation on tablet only) were re-run in isolation on a fresh disposable stack afterward
     (8/8 clean, then a further 3× `--repeat-each` clean run) and did not reproduce — classified
     as one-off harness flakiness from the long combined run, not defects.
   - **One scratch-test failure reproduced deterministically 3/3 times in isolation and is a real,
     newly-discovered `PRODUCT_DEFECT`** — see below.

### New finding: `/api/me/markpoint/*` also 401s for a legacy-bridged token

Confirmed independently via direct backend `curl` (bypassing the browser entirely, to rule out
any frontend/timing explanation), using the same real legacy-PIN-bridged token
(`POST /api/auth/login {"player_id":1,"pin":"1234"}`) this whole axis is about:

| Endpoint | Result (5/5 or 4/4 repeats, 100% consistent) |
|---|---|
| `GET /api/me/notifications` | 401 (already known, already fixed by this remediation) |
| `GET /api/me/markpoint/projection?family_id=1` | **401** |
| `GET /api/me/markpoint/weekly?family_id=1` | **401** |
| `GET /api/me/markpoint/level?family_id=1` | **401** |
| `GET /api/me/markpoint/deductions/history?family_id=1` | **401** |
| `GET /api/account-context` (same token) | 200 (works — uses the legacy-bridge-aware resolver) |

Root cause (read, not guessed): `backend/app/domains/markpoint_target/router.py`'s own `_me`
dependency (used by every `/api/me/markpoint/*` route) resolves the caller via
`get_current_account` from `backend/app/domains/family/dependencies.py` — a **strict,
Account-native-only** resolver whose own module docstring states it explicitly: "the Target
replacement for the legacy `get_current_user` -> `LegacyIdentityMapping` -> Account chain.
**Nothing here reads a legacy `player_auth`/`admin_auth` row or `legacy_identity_mappings`**".
This is the *same* dependency `/api/me/notifications` uses (confirmed: both routers depend on it).
`/api/account-context` instead uses the separate, legacy-bridge-aware `resolve_current_account` in
`backend/app/domains/family/service.py`. The two resolvers disagree on whether a legacy-PIN token
is a valid caller at all — `/api/me/notifications` was the one instance of this disagreement the
original Combined QA found and this remediation fixed; the four `/api/me/markpoint/*` routes are
the same disagreement, still live, previously undetected because the original Combined QA's own
"Markpoint transition" cross-domain check (see its own report, "tested by going directly to
`/family/members`/`/markpoint`... for a **single-family account, `member.a`**") used an
Account-native session for that specific step, never a legacy-bridged one.

**Real-browser consequence** (reproduced 3/3 in an isolated re-run, not a one-off): a legacy-PIN
multi-family session that survives the notifications-401 on `/family` (per the fix that *was*
made) and then does exactly what this task's own script requires next — "Markpoint 이동" — hits
`getLevel()`/`getProjection()`/`getWeekly()`/`getDeductionHistory()` inside
`MarkpointUser.tsx`'s own `Promise.all` load, all four 401, none of the four is (nor, being core
personal data rather than a decorative feature, should casually become) an
`OPTIONAL_ACCOUNT_ENDPOINTS` entry, and `httpClient.ts`'s global interceptor clears the whole
session and hard-redirects to `/` — reproducing, on the very next screen, the exact class of
symptom this remediation was supposed to have closed for good. Confirmed via a real DOM snapshot:
after `page.goto('/markpoint')`, the page is the unauthenticated profile-selector, not Markpoint.

This is **new** — not disclosed by the original FAIL report, not in either remediation's stated
scope, and not something this read-only QA session fixed.

### Isolated confirmation that other suspected failures were NOT reproducible

To avoid over- or under-reporting, three targeted re-runs were performed on a fresh, single-project
disposable stack after the 3-viewport run:
- 8× repeat of "select a Family then hard-navigate to `/markpoint`, admin nav CTA visible" — **8/8
  passed**, confirming the one 3-viewport-run failure of this shape was a harness artifact, not a
  reproducible defect.
- 3×`--repeat-each` of the full scratch Axis A/B spec on `desktop-1180x820` alone — reproduced the
  notification-then-markpoint 401 (3/3) and the family-switcher false-positive (3/3) exactly as
  above, and did **not** reproduce the nav/CTA-click or reload-preservation failures seen only in
  the 3-viewport run (0/3) — consistent with those being one-off flakiness under that heavier,
  longer run rather than defects.
- A direct, non-`page.reload()`-based re-check of "a genuine `/api/players` 401 clears the
  session": end state confirmed correct (URL settles at `/`, `sessionStorage.accessToken` is
  `null`) once the check stopped relying on Playwright's `reload()` navigation promise (which
  races against the interceptor's own `window.location.href` redirect and can time out even
  though the app's own end state is correct). This is reported as a **test-construction
  fragility** in the committed test itself (`01-shell.spec.ts`'s new "a genuine protected-endpoint
  401 still clears the session"), not a product defect — the underlying contract holds.

## Static checks

`git diff --check`: exit 0 (both before and after this session's own work). `python3
agent-system/tools/check_all.py`: all WARNINGs pre-date this task (the same ones already listed
in the prior FAIL report as pre-existing); zero new WARNING attributable to this task's own
changes (this task made none to product/test code).

## DB and runtime cleanup

All disposable databases (`mc_w74_qa_re_native`, `mc_w74_qa_re_pytest`, `mc_w74_qa_diag`,
`mc_w74_qa_flake`) dropped. All backend/frontend/Playwright/Chromium processes this session
started were killed (confirmed via `ps aux` — none remain). All scratch files
(`tests/e2e/playwright.qa-w74-re.config.ts`, `tests/e2e/run-qa-w74-re-native.sh`,
`tests/e2e/specs-mongle-scratch/`, `tests/e2e/test-results/`,
`tests/e2e/.runtime/qa-w74-re-native/`) deleted — confirmed via `git status --short` showing
exactly the original 7-file diff and nothing else. The pre-existing, unrelated database
`mc_qa_markpoint_reqa_001` on the same native Postgres cluster was **never touched** (not read,
not dropped) — its origin is unknown to this session and it does not match any database name this
session created; flagged for PM attention in the Handoff since a stale disposable-looking DB left
on a shared native cluster is itself a minor hygiene risk for a future session.

## Changes

Zero product-code changes. Zero test-file changes. This file and its paired Handoff are the only
two files this session leaves behind in the real repository. Zero commits, zero pushes.

## Axis verdicts

| Axis | Verdict |
|---|---|
| Markpoint Admin | **PASS** |
| Notification Session | **FAIL** |
| ActiveFamily | **PASS** |
| Cross-domain | **FAIL** |

## Overall verdict: FAIL

`Markpoint Admin` and `ActiveFamily` are both genuinely closed: real owner/admin direct access,
real nav/CTA access (on the viewport widths where the nav item exists at all — see Next Action),
member/unauthenticated denial, reload, back/forward, and cross-family isolation for Markpoint
Admin; real picker/storage/reload/nav-persistence/account-isolation/stale-value/malformed-value/
single-family-regression coverage for ActiveFamily, all via genuine unmocked browser flows,
matching or exceeding this task's own required scenario list.

`Notification Session` and `Cross-domain` cannot be PASS: the fix that *was* made
(`/api/me/notifications` → `OPTIONAL_ACCOUNT_ENDPOINTS`) is itself correct and independently
verified, but this task's own required flow ("Markpoint 이동 → 다른 protected API 200") fails on
a real, reproducible, previously-undisclosed defect in the very next step — `/api/me/markpoint/*`
also rejects the same legacy-bridged token, and a global session-clear fires there instead. This
is a `PRODUCT_DEFECT`, not an `ENVIRONMENT_FAILURE`, so this is reported as FAIL rather than
CONDITIONAL.

## Next action

1. A dedicated implementation task should extend the identity-resolution fix already applied once
   to `/api/me/notifications` to the four `/api/me/markpoint/*` routes' own `_me` dependency (or
   to `get_current_account` itself) — the product decision of *whether* a legacy-bridged session
   should see real Markpoint personal data (fix the resolver so it succeeds) or *should not* (in
   which case the frontend needs a graceful, session-preserving denial rather than a global
   logout, mirroring the `OPTIONAL_ACCOUNT_ENDPOINTS` shape) is a PM/architecture call this QA
   session does not make unilaterally, per the same reasoning the original FAIL report used for
   the notifications case.
2. A separate future Independent QA session (not the implementer) re-verifies the Notification
   Session and Cross-domain axes specifically once that fix lands.
3. `01-shell.spec.ts`'s pre-existing `loginAsFirstPlayer()` helper (`button[class*="playerCard"]`)
   should be corrected to match the current `ProfileSelectorScreen` markup — out of this
   read-only QA's scope to fix, but it currently blocks all 20 tests in the file, including the
   two this remediation added.
4. The new "a genuine protected-endpoint 401 still clears the session" test in the same file
   should stop relying on `page.reload()`'s own navigation promise (races against the
   interceptor's `window.location.href` redirect) — a test-maintenance item, not a product defect.
5. PM should confirm the origin of the pre-existing `mc_qa_markpoint_reqa_001` database on the
   shared native Postgres cluster; this session did not create it and did not touch it.
6. `/markpoint/admin`'s only real nav/CTA entry point is the desktop-width shell nav
   (`≥768px`, per `MongleAppShell.module.css`'s own `max-width: 767px` breakpoint) — the mobile
   bottom dock is a fixed, hardcoded 3-item list (마크포인트/와글와글/가족) with no admin entry at
   all, per that component's own pre-existing code comment
   (`PM_DECISION_REQUIRED_BOTTOM_DOCK_ROUTE`). This is confirmed pre-existing and out of this
   remediation's scope, not a regression, but worth a PM decision on whether Markpoint Admin
   should ever be reachable by nav on mobile (direct URL entry already works there today).
