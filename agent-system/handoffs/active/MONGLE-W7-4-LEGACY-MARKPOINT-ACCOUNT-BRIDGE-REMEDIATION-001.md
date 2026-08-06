# Session Handoff — MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-REMEDIATION-001

- Task ID: `MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-REMEDIATION-001`
- Role: Developer
- Status: `DEVELOPER_SELF_CHECK_COMPLETE` / `READY_FOR_LEGACY_MARKPOINT_FOCUSED_INDEPENDENT_RE_QA`
- Full detail: `agent-system/qa/MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-REMEDIATION-001.md`

## What changed

One file, minimal diff: `backend/app/domains/markpoint_target/router.py`'s private `_me`
dependency (shared by all nine `/api/me/markpoint/*` GET routes) now resolves the caller through
`get_current_user` + `family_service.resolve_current_account` — the same legacy-bridge-aware pair
`/api/account-context` already uses — instead of the strict, Account-native-only
`get_current_account`. A legacy-PIN session with a real canonical Account mapping and an active
Family membership can now reach Markpoint's own core data without 401ing and forcing the global
HTTP interceptor to destroy the session.

`get_family_membership` (shared by many other domains) and `get_current_account` itself (which
Wagle's realtime gateway deliberately depends on staying legacy-exclusive, D3) were **not**
touched — confirmed both by the diff itself and by two new dedicated regression tests.

## Why this was needed

The immediately preceding Independent Re-QA
(`MONGLE-W7-4-MARKPOINT-SESSION-ACTIVEFAMILY-COMBINED-FOCUSED-INDEPENDENT-RE-QA-001`, same
session, FAIL verdict) found that fixing `/api/me/notifications` alone was not enough: a
legacy-PIN multi-family session that survives that specific 401 and then does the natural next
thing — navigates to `/markpoint` — hit the identical class of defect one screen later, because
Markpoint's own `/api/me/markpoint/*` routes used a different, stricter identity resolver.

## Evidence highlights

- Baseline reproduced twice via direct backend `curl` (bypassing the browser): all nine
  `/api/me/markpoint/*` GET routes 401 for a real legacy-PIN token, before the fix.
- Post-fix: same nine routes 200, twice, plus a full Account-native regression check (also 200,
  unchanged) and an identity-parity check proving the legacy bridge and a native login for the
  *same* person return byte-identical real data.
- 28 new focused backend tests, full 439/439 backend suite (this task changed backend code, so the
  full suite was run rather than a targeted subset), and an 18/18 real-browser Playwright run at
  all three required viewports (the full flow: notification-401-survives → Markpoint core APIs
  200 → real DOM; Account-native regression; genuine-401 still clears the session; Markpoint Admin
  regression; ActiveFamily regression).

## What this task does NOT claim

Per its own Section 18 instruction, this Developer self-check does **not** overwrite the prior
Independent Re-QA's FAIL verdict for Notification Session / Cross-domain. Those stay FAIL until a
separate, fresh Independent QA session (not this one, not the implementer) reproduces this
result independently.

## Suggested next Task

`MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-FOCUSED-INDEPENDENT-RE-QA-001` (or similar) — a fresh
Independent QA session verifying this fix, re-confirming Notification Session and Cross-domain PASS
end to end, before either axis is claimed PASS in governance.

## Cleanup confirmation

All disposable databases (`mc_w74_bridge_repro`, `mc_w74_bridge_pytest`, and the browser
self-check's own `mc_w74_bridge_selfcheck`) dropped. All backend/frontend/Playwright/Chromium
processes killed. All scratch config/launcher/spec files removed —
`git status --short` shows exactly: the two prior remediations' 7 files (unchanged), the prior
Re-QA's 2 documents (unchanged), this task's own 1 product file + 1 new test file, and this
document pair plus the `active.md`/`relay/current.md` append-only entries. `mc_qa_markpoint_reqa_001`
(unexplained, flagged by the prior Re-QA) was not touched. No commit, no push.
