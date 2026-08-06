# Session Handoff — MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001

- Task ID: `MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001`
- Role: Independent QA Engineer (fresh session, read-only on product/test code)
- Verdict: **PASS** — see the paired QA Evidence at `agent-system/qa/
  MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001.md` for full detail;
  this file summarizes state and next steps for whoever picks this up.

## What this task verified

The Developer remediation reported in `MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-
REMEDIATION-001` (self-check only, not independent) — swapping the private `_me` dependency
shared by all nine `/api/me/markpoint/*` GET routes from the strict, Account-native-only
`get_current_account` to the same legacy-bridge-aware `get_current_user` +
`resolve_current_account` pair `/api/account-context` already uses. This closes the gap the
immediately preceding Independent Re-QA (`MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-
FOCUSED-INDEPENDENT-RE-QA-001`, FAIL) found: a legacy-PIN session that survived the
already-fixed `/api/me/notifications` 401 hit the identical class of defect one screen later on
real Markpoint data.

1. Legacy Markpoint Bridge (Axis A, real HTTP): **PASS** — all 9 endpoints 200 for a legacy
   token, correct family scope, safe rejection for no-mapping/not-linked/no-membership/no-
   permission, 403+zero-leak for cross-family, 401 for unauthenticated/forged, both blast-radius
   guards (admin route, Wagle realtime) confirmed still legacy-exclusive as designed, identity
   parity confirmed between legacy and native logins for the same person.
2. Notification Session (Axis B, real browser): **PASS** — the notification-only 401 still
   preserves the session (prior fix, re-confirmed), and the real next step, navigating to
   `/markpoint`, now succeeds with real 200s and a real rendered DOM instead of a forced logout.
   A genuine, unrelated 401 still correctly destroys the session.
3. Cross-domain (Axis C, real browser, full flow): **PASS** — completed end to end (login →
   family select → notification 401 → Markpoint → reload → back/forward → logout) with no
   cross-family leakage, at all 3 required viewports.
4. Prior-PASS regression (Markpoint Admin, ActiveFamily): **PASS**, no regression.

## State of the repository

Unchanged from before this session in shape: the same 10-modified/5-untracked uncommitted diff on
`dev-newmarkp` (`git status --short` identical before and after, independently re-verified — see
the QA Evidence's own "Independent re-verification of cleanup" section). This session made
**zero** product or test code changes, zero commits, zero pushes. The two new QA/handoff files
(this one and its pair) plus append-only entries to `agent-system/active.md`/`agent-system/
relay/current.md` are the only additions.

## Execution note for whoever reads this

The runtime/browser verification (disposable DB, throwaway backend+frontend, real Playwright
across 3 viewports, full backend suite) was carried out by a delegated sub-session under this
session's direct specification. That sub-session twice ended its turn on an ambiguous
"waiting for pytest" status instead of reporting a real result — traced to a `run_in_background`
usage pattern that didn't reliably surface completion back to it. It was told to stop, given no
further verification work, and ordered to clean up and report exactly what it had already
verified with real evidence versus what was left incomplete. Its cleanup claims were then
independently re-run and confirmed by this session before trusting them (see QA Evidence). One
item — a standalone per-file breakdown of 9 "related targeted backend" test files — was
interrupted mid-run by that stop order and is reported as `NOT RUN` standalone in the QA Evidence
rather than backfilled as PASS; it is still proven by the completed 439/439 full-suite run, which
includes all 9 of those files.

## Minor finding, not blocking

`tests/README.md` still documents the frontend package manager as `npm`. The frontend finished
migrating to `pnpm` in commit `0319940` (`frontend/package.json` has
`"packageManager": "pnpm@10.32.1"`, only `pnpm-lock.yaml` is present). Doc drift, not a product
defect — flagged for a future documentation task.

## Suggested next Task

A Branch Integration task to commit the now-fully-independently-PASS-verified bundle (this
task's `router.py` fix + new test, plus the two prior remediations it built on), subject to PM
commit-scope review. Separately: `01-shell.spec.ts`'s `loginAsFirstPlayer()` stale locator and its
genuine-401 test's `page.reload()` race remain open test-maintenance items; `tests/README.md`'s
npm→pnpm drift is a separate doc-maintenance item; PM should confirm the origin of the still
unexplained `mc_qa_markpoint_reqa_001` database, observed and left untouched by three consecutive
independent QA sessions now.

## Cleanup confirmation

All disposable databases (`mc_w74_indqa_r7x9`, `mc_w74_indqa_r7x9_pytest`) dropped — confirmed via
a direct `pg_database` query showing zero `mc_w74*` rows. All backend/frontend/Playwright/
Chromium processes started by this task's work killed — confirmed via `ps aux`, only one
pre-existing, unrelated `vite --port 5299` process (predates this session) remains, untouched.
All scratch files (`tests/e2e/.runtime/w74-indqa/`, `tests/e2e/test-results/`) deleted — confirmed
via directory listing showing only other tasks' pre-existing sibling directories remain.
`git stash list` empty. `mc_qa_markpoint_reqa_001` not touched. No commit, no push.
