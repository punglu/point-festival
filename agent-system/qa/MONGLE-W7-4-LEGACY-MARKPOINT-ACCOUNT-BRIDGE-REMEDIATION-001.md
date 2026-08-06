# Developer Self-Check — MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-REMEDIATION-001

- Task ID: `MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-REMEDIATION-001`
- Role: Developer (same session that produced the preceding Independent Re-QA FAIL report;
  this document is a **Developer self-check**, not an Independent QA verdict — see Governance
  below)
- observed_at: 2026-08-07
- git_ref: `5ba398c` (branch `dev-newmarkp`) plus the same still-uncommitted 9-file remediation
  diff from before, now with `backend/app/domains/markpoint_target/router.py` (product fix) and
  `backend/tests/test_markpoint_legacy_account_bridge_wave7.py` (new focused tests) added on top
- Verdict: **DEVELOPER_SELF_CHECK_PASS** (own scope only — see Governance)
- Commit/push: 0

## PM_CONFIRMED baseline

Starting axis state, per `MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-
INDEPENDENT-RE-QA-001`: Markpoint Admin PASS, Notification Session FAIL, ActiveFamily PASS,
Cross-domain FAIL. This task addresses the specific root cause that report found: legacy-PIN
sessions 401 on Markpoint's own core `/api/me/markpoint/*` routes, one screen past the already-
fixed `/api/me/notifications`.

## Start Gate

`pwd` → `/appl/point-festival`; `git branch --show-current` → `dev-newmarkp`; `git rev-parse HEAD`
→ `5ba398c...`; `git status --short` matched the PM-reported 9-file dirty set exactly (7
product/test files from the two prior remediations + the 2 Re-QA doc files this same session's
earlier QA phase produced); `git diff --check` clean; `git stash list` empty; `git fetch --prune`
→ no divergence, `@{u}` identical to HEAD. Classification: all 7 pre-existing files → A (Markpoint/
notification remediation) or B (ActiveFamily remediation); the 2 QA doc files → C (Independent
Re-QA tracking). No D/E/F. No `reset`/`clean`/`restore`/`stash`(destructive)/`merge`/`rebase`/
`commit`/`push` was run — the one `git stash push -- backend/.../router.py` used during Baseline
Reproduction (below) was immediately `pop`ped back, confirmed via `git status --short` before and
after.

## Authority Discovery

Full authentication/identity trace read directly from current code (not from any prior report):
`markpoint_target/router.py`'s own `_me` dependency; `family/dependencies.py` (`get_current_account`,
`get_family_membership`); `app/dependencies.py` (`get_current_user`); `family/service.py`
(`resolve_current_account`, `_legacy_identity`, `get_active_membership`); `family/router.py`
(`/api/account-context`'s own real usage of `get_current_user` + `resolve_current_account`);
`wagle/realtime_router.py` (every route also depends on `get_current_account`, confirming its
strict-Account-native design is load-bearing elsewhere, not incidental).

## Baseline Reproduction

Fresh disposable native Postgres (`mc_w74_bridge_repro`), the repo's own official seed
(`phase1_seed_synthetic.py`), native backend (no Docker in this WSL session). To reproduce on the
**true** pre-fix baseline without losing the two prior remediations' own changes, only
`backend/app/domains/markpoint_target/router.py` was `git stash push`-ed for the duration of this
step (confirmed via `git status --short` immediately before and after: nothing else moved), then
`pop`-ped back before any implementation began.

Legacy account/profile: legacy player 1 (유빈, PIN `1234`) → its own `LegacyIdentityMapping`
bridges it to Account `owner.a` (Family Alpha `mission_manager`, per the seed). Token type:
real `POST /api/auth/login` JWT (`role: player`). Family/membership: Family Alpha, active.

Endpoint inventory (all nine `/api/me/markpoint/*` GET routes sharing the one `_me` dependency,
not just the four the frontend's own `Promise.all` calls):

| Endpoint | Baseline (pre-fix), legacy token, ×2 | Account-native token (comparison) |
|---|---|---|
| `missions` | 401 / 401 | 200 |
| `ledger` | 401 / 401 | 200 |
| `balance` | 401 / 401 | 200 |
| `level` | 401 / 401 | 200 |
| `summary` | 401 / 401 | 200 |
| `deductions` | 401 / 401 | 200 |
| `weekly` | 401 / 401 | 200 |
| `projection` | 401 / 401 | 200 |
| `deductions/history` | 401 / 401 | 200 |

Reproduced twice as required, both direct-backend `curl` (bypassing the browser to isolate the
backend contract) — 401 both times for every one of the nine, 200 for the Account-native
comparison token on all nine. `/api/account-context` with the *same* legacy token: 200 (confirms
the legacy bridge itself is real and working — the defect is specific to `_me`'s own resolver
choice, not the bridge or the token).

## Root Cause

1. **Dependency**: `_me` (private to `markpoint_target/router.py`, shared by all nine
   `/api/me/markpoint/*` GET routes) used `Depends(get_current_account)` from
   `family/dependencies.py`.
2. **What that dependency allows**: only a token whose `resolve_account_from_session_claim` finds
   a live Account `Session` claim (`sid`) — its own module docstring: "Nothing here reads a legacy
   `player_auth`/`admin_auth` row or `legacy_identity_mappings`". A legacy-PIN token has no such
   claim.
3. **Legacy token claim**: `{"sub": "<player_id>", "role": "player", ...}` — decoded by the
   *generic* `get_current_user` (`app/dependencies.py`), which explicitly accepts
   `player`/`admin`/`account` roles together, precisely so downstream code can bridge them.
4. **`/api/account-context`'s own bridge**: `Depends(get_current_user)` in the route signature,
   then an explicit in-body call to `service.resolve_current_account(db, user)` — the same
   two-step pattern repeated for `create_family`/`list_families`/`get_family`/`update_family` in
   the same router file (confirmed by direct `grep`, not assumed).
5. **Other legacy-aware consumer**: `require_admin`'s Account→admin bridge
   (`is_account_linked_to_admin`, `app/dependencies.py`) reuses the exact same
   `resolve_account_from_session_claim` plus `LegacyIdentityMapping` lookup shape.
6. **Why Markpoint couldn't just reuse `get_current_account`**: it is also the dependency every
   Wagle realtime route uses (`wagle/realtime_router.py`, 10 usages, confirmed by `grep`), where
   staying strictly Account-native is a deliberate D3 design decision (a legacy token there is
   *meant* to 401) — widening `get_current_account` itself would have silently changed Wagle's
   own contract too.
7. **Family scope**: resolved identically before and after this fix —
   `family_service.get_active_membership(db, account.id, family_id)`, called with whichever
   `account.id` the (now-correct) resolver produced.
8. **Mapping/membership failure status**: unchanged, both already-established — 403 "계정 매핑이
   필요합니다" (from `resolve_current_account`, existing contract) and 403 "활성 가족 구성원 권한이
   필요합니다" (from `get_active_membership`, existing contract).

Classification: **STRICT_ACCOUNT_NATIVE_DEPENDENCY** (primary) + **DUPLICATED_IDENTITY_RESOLVER**
(the codebase already has two working identity resolvers for this exact case; `_me` had simply
picked the wrong one for a "core, both-credential-systems" route).

## Canonical Bridge Selection

Reused `get_current_user` (`app/dependencies.py`) + `family_service.resolve_current_account`
(`family/service.py`) — the exact pair `/api/account-context` and three sibling routes in the same
file already call, and the same underlying Account-session check
(`resolve_account_from_session_claim`) `get_current_account` itself uses for the Account-native
branch, so Session-liveness/Account-active semantics stay in the one place they already lived.
**No new resolver, no new identity bridge, no duplicated logic** — `_me` now calls two existing,
already-proven functions instead of one. `get_family_membership` (shared by `family_schedule`,
`family_todo`, `family_album`, `reward_catalog`, `family_search`, `family_rules`,
`markpoint_access`, and every `/api/families/{id}/markpoint/*` admin/mutation route in this same
file) and `get_current_account` itself were both **confirmed left untouched** — neither appears in
the diff, and both are separately exercised by this task's own new regression tests (below) to
prove their behavior is unchanged.

## Implementation

**Product file**: `backend/app/domains/markpoint_target/router.py` only. `_me`'s signature changed
from `account: Account = Depends(get_current_account)` to `user: dict = Depends(get_current_user)`,
with one added line, `account = await family_service.resolve_current_account(db, user)`, before
the unchanged `get_active_membership` call. Import changes: added `get_current_user`
(`app.dependencies`); removed `get_current_account` and the now-unused `Account` model import
(nothing else in the file referenced either). `get_family_membership` import unchanged. Total diff:
**17 insertions, 3 deletions, one file** (`git diff --stat`).

**Test file**: `backend/tests/test_markpoint_legacy_account_bridge_wave7.py` (new, 28 tests) —
see Backend Regression Matrix below.

**Why minimal**: the fix is a two-line body change plus an import swap, confined to one private,
router-local helper function with exactly nine call sites, all in the same file, all already
covered by the new focused tests. No router gained new business logic (the two calls `_me` now
makes are the same two calls `/api/account-context` already makes, in the same order); no shared
dependency, no other domain's router, no frontend file, no migration, no RBAC/permission seed, and
no Markpoint calculation logic was touched.

## Endpoint Matrix

All nine `/api/me/markpoint/*` GET routes, legacy-PIN token (owner.a via player 1), Family Alpha:

| Endpoint | Legacy before | Legacy after | Account-native | Mapping missing | Membership missing | Access/permission missing | Cross-family | Unauthenticated |
|---|---|---|---|---|---|---|---|---|
| missions | 401 | 200 | 200 | 403 | 403 | 403 | 403 | 401 |
| ledger | 401 | 200 | 200 | — | — | — | — | — |
| balance | 401 | 200 | 200 | — | — | — | — | — |
| level | 401 | 200 | 200 | 403 | 403 | 403 | 403 | 401 |
| summary | 401 | 200 | 200 | — | — | — | — | — |
| deductions | 401 | 200 | 200 | — | — | — | — | — |
| weekly | 401 | 200 | 200 | — | — | — | — | — |
| projection | 401 | 200 | 200 | — | — | — | — | — |
| deductions/history | 401 | 200 | 200 | — | — | — | — | — |

(Full per-endpoint mapping/membership/access/cross-family/unauthenticated matrix asserted for
`level` and `missions` explicitly in the new test file since all nine share the identical `_me`
dependency and downstream `require_access`/`get_active_membership` calls; a forged token was
additionally checked once, 401.) A dedicated identity-parity check confirmed the legacy bridge and
an Account-native login for the *same* underlying person return byte-identical, real (non-empty)
mission data — not a divergent or fabricated result.

## Browser Result

Real, unmocked Playwright run (native no-Docker stack, disposable Postgres, 3 required viewports,
`--workers=1`) — 18/18 passed at 390×844, 820×1180, and 1180×820:

- **Legacy login → family selection → `GET /api/me/notifications` real 401 → session survives
  (token present, no redirect) → `/markpoint` → all four of `projection`/`weekly`/`level`/
  `deductions/history` observed at real HTTP 200 via `page.on('response')` → real DOM (`포인트
  잔치` heading, balance/level/remaining testids visible) → `sessionStorage.accessToken` still
  present, `mc_session_expired` still absent.** This is the exact flow this task's own Section 13.1
  and the prior Independent Re-QA's required scenario both specify.
- **Account-native regression**: `owner.a` → `/markpoint` → same real heading/data, session intact.
- **Genuine protected 401**: a real 401 forced on `/api/players` (unrelated to Markpoint) still
  clears `sessionStorage.accessToken` and settles the URL at `/` — the global 401 contract was not
  weakened by this fix.
- **Markpoint Admin regression** (prior PASS axis): `owner.a` → `/markpoint/admin` → real
  `admin-mission-table` visible; `member.a` → `/markpoint/admin` → `markpoint-admin-denied` shown,
  not the admin table.
- **ActiveFamily regression** (prior PASS axis): `owner.a`'s Family selection survives
  `page.reload()` and persists into `/markpoint`.

## Tests

- New focused tests: `test_markpoint_legacy_account_bridge_wave7.py` — **28/28 passed** (all nine
  GET endpoints × legacy token; identity-parity; all nine × Account-native regression; mapping-
  missing; mapping-not-yet-linked; membership-missing; cross-family; inactive-subscription-403;
  no-token-401; forged-token-401; two blast-radius guards confirming `get_family_membership` and
  `get_current_account` are both unaffected).
- Full Backend pytest: **439 passed, 0 failed**, 757.92s, disposable native Postgres — this is the
  entire suite, not a subset, run because backend code changed (Section 16 requires this over the
  targeted-subset shortcut used when backend diff is 0).
- Frontend lint: clean. Typecheck/build (`tsc -b && vite build`): clean, 668 modules, only the
  pre-existing >500kB chunk advisory.
- Focused Playwright (browser self-check): 18/18, see above.
- `git diff --check`: clean.
- `check_all.py`: zero new warning class; the only new lines are this task's own "COMPLETED but
  remains active" / "Closeout Synchronization block is missing" / "missing a valid Verdict" for
  the *prior* Re-QA task's own FAIL-verdict document (a pre-existing checker-tool gap — its
  whitelist is `{PASS, CONDITIONAL, BLOCKED, HUMAN_GATE}` and does not include `FAIL`, confirmed
  by reading `check_closeout.py` directly — not something this task introduced or should silently
  "fix" by relabeling a real FAIL as something else).

## DB/Runtime Cleanup

Baseline-reproduction DB (`mc_w74_bridge_repro`), the disposable player-5 (no-mapping) fixture row
inserted into it, and the two focused-test DBs (`mc_w74_bridge_pytest`, plus the browser
self-check's own `mc_w74_bridge_selfcheck`, dropped automatically by its own launcher script's
`trap cleanup EXIT`) were all dropped — confirmed via `psql -c '\l'` showing none remain. All
backend/frontend/Playwright/Chromium processes this session started were killed — confirmed via
`ps aux`. All scratch files (`tests/e2e/playwright.dev-w74-bridge.config.ts`,
`tests/e2e/run-dev-w74-bridge-selfcheck.sh`, `tests/e2e/specs-mongle-scratch/`,
`tests/e2e/test-results/`, the empty `.runtime/dev-w74-bridge-selfcheck/` directory) removed —
`git status --short` confirmed to show exactly the intended product/test/doc diff and nothing
else. `mc_qa_markpoint_reqa_001` (the unrelated, unexplained database flagged by the prior
Independent Re-QA) was **not** read, written, or used as a fixture by this task.

## Governance

- Markpoint Admin (Independent Re-QA verdict): **PASS, unchanged** — this task did not touch its
  route, its component, or its tests, and this task's own regression check confirms it still
  renders real content for owner/admin and still denies a plain member.
- ActiveFamily (Independent Re-QA verdict): **PASS, unchanged** — same non-touch + regression-check
  basis.
- Notification Session: the prior Independent Re-QA's **FAIL verdict is not overwritten by this
  Developer self-check**. This task's own browser evidence shows the full required flow passing
  end to end, but per this task's own Section 18 instruction and this repository's Independent QA
  discipline, a Developer's own self-check is not Independent QA — the FAIL stays FAIL until a
  separate, fresh Independent QA session reproduces this result independently.
- Cross-domain: same — not overwritten; awaits the same future Independent QA.
- Legacy Markpoint bridge (this task's own scope): **DEVELOPER_SELF_CHECK_PASS**.

## Changes

Product: `backend/app/domains/markpoint_target/router.py` (1 file, 17 insertions / 3 deletions).
Test: `backend/tests/test_markpoint_legacy_account_bridge_wave7.py` (1 new file, 28 tests). No
other product or test file touched — the seven files from the two prior remediations and the two
prior Re-QA documents are byte-for-byte what this task started with. Documents: this file, its
paired Handoff, and append-only entries in `active.md`/`relay/current.md`. Zero commits, zero
pushes.

## Final status

```text
DEVELOPER_SELF_CHECK_COMPLETE
READY_FOR_LEGACY_MARKPOINT_FOCUSED_INDEPENDENT_RE_QA
```
