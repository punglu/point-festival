# Session Handoff — MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001

- Task ID: `MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001`
- Role: Independent QA Engineer (fresh session, read-only on product/test code)
- Verdict: **FAIL** — see the paired QA Evidence at `agent-system/qa/
  MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001.md` for full
  detail; this file summarizes state and next steps for whoever picks this up.

## What this task verified

Three contracts remediated after the prior `MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-FOCUSED-
INDEPENDENT-QA-001` FAIL report (`agent-system/qa/MONGLE-W7-4-AUTH-FAMILY-MARKPOINT-COMBINED-
FOCUSED-INDEPENDENT-QA-001.md`):

1. `/markpoint/admin` route registration and permission — **confirmed fixed, PASS**.
2. Legacy notification-only 401 session integrity — **the specific fix made is correct, but the
   contract as a whole is still broken one step later — FAIL**.
3. Multi-family `activeFamily` storage/restore — **confirmed fixed, PASS**.

## State of the repository

Unchanged from before this session: the same 7-file uncommitted diff on `dev-newmarkp`
(`git status --short` identical before and after). This session made **zero** product or test
code changes, zero commits, zero pushes. The two new QA/handoff files (this one and its pair) are
the only additions.

## The one thing that must not get lost

The remediation's own fix (`/api/me/notifications` → `OPTIONAL_ACCOUNT_ENDPOINTS`) is real and
correct — do not revert it. But it does not close the underlying contract on its own: the very
next real-world step in the same user journey ("Markpoint 이동") independently 401s on **four**
different `/api/me/markpoint/*` endpoints for the same legacy-bridged token, because those routes
use a different, stricter, Account-native-only identity resolver
(`get_current_account` in `backend/app/domains/family/dependencies.py`) than the one
`/api/account-context` uses. This was confirmed with direct backend `curl` (bypassing the browser
entirely) and reproduced 3/3 times in an isolated Playwright re-run. See the QA Evidence's own
"New finding" section for the full root-cause trace and file/line pointers.

This is not something this session can decide how to fix (whether legacy-bridged users should get
real Markpoint data via a resolver fix, or a graceful non-logout denial via the
`OPTIONAL_ACCOUNT_ENDPOINTS` shape) — that is a PM/architecture call, same as the original FAIL
report deferred the equivalent decision for notifications itself.

## Suggested next Task IDs

- `MONGLE-W7-4-MARKPOINT-ME-ENDPOINTS-LEGACY-BRIDGE-REMEDIATION-001` (or similar) — fix the
  `/api/me/markpoint/*` identity-resolution gap once a PM decision on intended behavior is made.
- A follow-up `...-FOCUSED-INDEPENDENT-RE-QA-002` (fresh session, not the implementer) to
  re-verify Notification Session + Cross-domain once that lands.
- Separately, unrelated to this task's own scope but discovered along the way:
  `01-shell.spec.ts`'s `loginAsFirstPlayer()` helper needs its stale `button[class*="playerCard"]`
  locator corrected (blocks 20/20 tests in that file today); its new "genuine protected-endpoint
  401" test should stop depending on `page.reload()`'s own navigation promise.

## Environment notes for the next session

No Docker in this WSL environment. A native Postgres cluster is already running at
`127.0.0.1:5432` (`mc_admin`/`mc_local_dev_2026`) with a working `backend/.venv` — the repo's own
`tests/e2e/scripts/run-w75-full-spec-native.sh` is a working template for a native, no-Docker
Playwright run against a disposable database; this session's own (deleted) scratch launcher was a
direct copy of that pattern retargeted at different spec files and a 3-viewport config, since the
committed native launcher hardcodes one spec file and the committed manual/Docker configs don't
offer the three required non-desktop viewports without Docker.

One unrelated, pre-existing database (`mc_qa_markpoint_reqa_001`) was observed on the same native
Postgres cluster; this session did not create or touch it and does not know its origin — PM should
confirm whether it is stale and safe to drop.

## Cleanup confirmation

All disposable databases dropped, all backend/frontend/Playwright/Chromium processes killed, all
scratch files removed (`git status --short` returns exactly the pre-existing 7-file diff). No
orphan processes, no leftover ports, no persistent/shared resources modified.
