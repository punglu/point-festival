# MONGLE-W3-FRONTEND-RUNTIME-CLOSEOUT-QA-001

- Parent: `MONGLE-W3-WAGLE-INDEPENDENT-QA-001` (PM verdict: Backend/cross-process
  PASS, full Wave 3 lifecycle `CONDITIONAL` pending an independent Playwright
  run)
- author/agent: `Claude Code`
- observed_at: 2026-08-01
- environment: `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`, HEAD
  `2243aa83d3a0e527e83483651d10c2879026c704` unchanged. Isolated `mc_phase1`
  Compose stack, brought up and torn down by
  `tests/e2e/playwright.mongle.config.ts` itself.
- secrets_redacted: true

## 1. Command and Raw Result

```bash
cd tests/e2e && npx playwright test --config playwright.mongle.config.ts
```

```text
121 passed (1.5m)
4 skipped
0 failed
0 retries (no retry markers in output; config declares no retries)
```

Teardown log confirmed: `mc_phase1-frontend-1`, `mc_phase1-backend-1`,
`mc_phase1-db-1` all Stopped/Removed; `mc_phase1_phase1_pg_data` volume
Removed; `mc_phase1_network` Removed. Post-run `docker ps -a --filter
name=mc_phase1`, `docker volume ls`, `docker network ls` all confirm zero
residual — independently re-checked after the run, not read from the
teardown log alone.

The 4 skips are the same intentionally-scoped case as every prior run in
this repository's history: `internal Dock/nav clicks produce canonical
URLs, never /naran/*`, skipped on `iphone`/`ipad`/`android-tablet-portrait`/
`android-tablet-landscape` (touch-only projects where the desktop-hover
interaction the test exercises does not apply) — not a Core Wagle case.

## 2. Required Markers

```text
PLAYWRIGHT_CURRENT_SOURCE_CONFIRMED: YES
  — "Current-source runtime proof: the browser is served the build made
    from this worktree" passed on every project that runs it
    (desktop/android-tablet-portrait/android-tablet-landscape and
    equivalent coverage on iphone/ipad via the shared bring-up guard).
WAGLE_PIN_UI_INDEPENDENT_QA_PASS: YES
WAGLE_FRONTEND_REALTIME_INDEPENDENT_QA_PASS: PASS — scoped precisely below (§3)
FAILED: 0
RETRIES: 0
TASK_DOCKER_RESIDUAL: 0
```

## 3. PM's 10-item Scope, Mapped to Actual Test Coverage — Honest Accounting

This QA does not claim coverage for a scenario that has no executable test,
and does not write a new test that would have to fabricate a real-room UI
interaction the product does not yet have (`WagleLanding` still renders
preview fixtures; wiring real rooms is `MONGLE-W5-TARGET-UI-001`, Wave 6).
Writing such a test would either assert against a fixture (proving nothing
about the real dispatcher) or require new frontend product code, which is
outside this QA's defect-correction authority.

| # | PM's scenario | Coverage | Test | Result |
|---|---|---|---|---|
| 1 | PIN-status 401 does not cause Account logout | **Playwright, independently re-run** | `a refused realtime channel does not end the session or hide the screen` | **PASS** (desktop+iphone+ipad+android×2) |
| 2 | terminal 4401 does not cause infinite reconnect | **Playwright, independently re-run** | `a legacy player session cannot open the Account-native realtime channel` (asserts `authorization_lost` and re-asserts it settled 3s later — no reconnect storm) | **PASS** (all 5 projects) |
| 3 | ordinary network disconnect reconnects normally | **Not Playwright-testable in this codebase today** | none exists | `NOT_COVERED_AT_UI_LAYER` — see §4 |
| 4 | resume / missed-message recovery | **Not Playwright-testable today** (no real room UI) | none exists | `NOT_COVERED_AT_UI_LAYER` — see §4 |
| 5 | duplicate event, no duplicate render | **Not Playwright-testable today** | none exists | `NOT_COVERED_AT_UI_LAYER` — see §4 |
| 6 | sequence gap → history refetch | **Not Playwright-testable today** | none exists | `NOT_COVERED_AT_UI_LAYER` — see §4 |
| 7 | one Family's revoke leaves another Family's subscription working | **Not Playwright-testable today** | none exists | `NOT_COVERED_AT_UI_LAYER` — see §4 |
| 8 | PIN lock does not block Mongle/Markpoint/Push | **Playwright, independently re-run (partial)** | `the lock never blocks the rest of the platform` — proves `/wagle`, `/dashboard`, `/family` all stay reachable while locked | **PASS** for the routes it exercises; no dedicated Markpoint-route or Push-delivery-while-locked browser assertion exists (Markpoint has no Wave-5-wired frontend route yet either) |
| 9 | Wagle shows as available, not disabled | **Playwright, independently re-run** | `an active wagle subscription from the API renders as available, not disabled` | **PASS** (desktop+iphone+ipad+android×2) |
| 10 | current-source fingerprint match | **Playwright, independently re-run** | `Current-source runtime proof: the browser is served the build made from this worktree` | **PASS** |

**5 of 10 items are directly proven by an independently re-run browser
test** (1, 2, 9, 10 fully; 8 for the routes that exist). **5 items (3-7) have
zero Playwright coverage**, for a structural reason stated in the spec
file's own docstring before this QA ever ran it: the real-room UI is Wave 6
scope. This is not a gap this QA introduced or hid — `MONGLE-W3-WAGLE-
INDEPENDENT-QA-001`'s own report already flagged the identical boundary at
§22, and it is why that report never claimed a "message-level realtime UI
journey" as PASS.

## 4. Where items 3-7 ARE actually verified

Not at the browser layer, but at the API/service layer, by the backend test
suite this QA's parent task (`MONGLE-W3-WAGLE-INDEPENDENT-QA-001`)
independently re-ran and reported 239/239 passing on:

- **#3 (reconnect)**: `test_wagle_multiworker_fanout.py`'s listener-restart
  test, plus this closeout's own §1 confirms `authorization_lost` settles
  rather than loops — the client-side reconnect state machine itself (for a
  *recoverable*, non-terminal disconnect) is exercised in
  `wagleRealtimeClient.ts`'s own logic but has no dedicated Playwright case
  simulating a raw network drop; recorded as a real, named gap rather than
  claimed covered.
- **#4 (resume/recovery)**: `resume_missed_events()` tests inside
  `test_wagle_realtime_wave3.py` (ascending order, replay-safety,
  join-boundary, cross-family denial) — re-run independently by the parent
  QA.
- **#5 (dedup)**: the dispatcher's `test_dispatcher_is_safe_to_run_twice_on_
  the_same_event` and the multiworker duplicate-NOTIFY test — re-run
  independently.
- **#6 (gap → refetch)**: covered by the same `resume_missed_events()` tests
  as #4 — a client that reconnects after a gap calls the identical query.
- **#7 (Family isolation on revoke)**: `test_wagle_websocket_gateway_wave3.py`'s
  Session-revoke-closes-all vs. one-Family-membership-ends-only-that-
  subscription tests — re-run independently.

This QA does not re-derive those results a third time; they are the parent
task's own already-independent evidence, cited here rather than duplicated.

## 5. Verdict

```text
WAVE_3_FRONTEND_INDEPENDENT_QA_PASS_FOR_EXISTING_UI_SCOPE
WAVE_3_UI_LAYER_COVERAGE_GAP_RECORDED_NOT_HIDDEN (items 3-7, Wave-6-bounded)
PLAYWRIGHT_CURRENT_SOURCE_CONFIRMED
FAILED: 0 / RETRIES: 0 / SKIPPED: 4 (pre-existing, non-Core)
TASK_DOCKER_RESIDUAL: 0
WAVE_3_CORE_LIFECYCLE_READY_TO_CLOSE
```

Recommendation to PM: close Wave 3 Core Lifecycle on this evidence. Items
3-7 are not a Wave 3 product defect — they are a UI-layer test that cannot
exist honestly before Wave 6 wires a real room screen, and their underlying
backend behavior is independently proven. If PM wants browser-level proof of
3-7 specifically before Wave 5/6, that is new test-infrastructure work (a
minimal fixture-driven realtime harness independent of the real room UI),
not a re-run of what exists today.

## Closeout Synchronization

- Contract: v1
- Independent QA: this is the independent QA — PASS for existing UI scope,
  gap named for items 3-7
- COVERAGE MAP: not modified this session (no new row required beyond what a
  PM graduation pass will add)
