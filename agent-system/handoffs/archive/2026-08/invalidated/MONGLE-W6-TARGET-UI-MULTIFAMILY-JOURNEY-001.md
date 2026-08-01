# INVALIDATED_DO_NOT_USE — MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001

Active authority retired by `MONGLE-W6-CANONICAL-UI-RECOVERY-BASELINE-001`.
See `agent-system/incidents/MONGLE-W6-NONCANONICAL-UI-INCIDENT-001.md`.

# Historical record

- Task ID: `MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`
- author/agent: `Claude Code`
- created_at: `2026-08-01`
- git_ref: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
- environment: isolated Compose project `mc_phase1`; frontend checks in `mongle-frontend-toolchain`
- evidence: `agent-system/qa/MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001.md`
- secrets_redacted: `true`
- Lifecycle: `FAIL`
- Decision: `DESIGN_APPROVED` (PM Wave 6 directive, 2026-08-01)
- Verification: `FAIL` (self-check)
- Execution: `PARTIAL_IMPLEMENTED`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
- End HEAD: same (unchanged — no commit)

## What works, verified in a real browser

All seven Wave 6 journeys pass on desktop — **15/15**, real API, no mocks, no
fixtures: multi-family switching with the session preserved, Markpoint user
figures matching the API, submit → pending, admin filter/bulk-approve/cycle
guard/materialize, two-browser Wagle realtime with exactly-once delivery and
offline recovery, PIN isolation, and both permission separations.

## What does not

```text
Playwright (5 projects) : 200 collected / 135 passed / 61 failed / 4 skipped / 0 retries
  desktop journeys      : 15/15 pass
  mobile+tablet         : 10 fail  — real responsive gaps
  01-shell, 02-wagle    : 51 fail  — legacy-premise specs superseded by this Wave
Visual deliverable      : NOT PRODUCED (§11 required 14 screens x 2 viewports)
Journey 5 (revoke)      : NOT_RUN — fixture cannot revoke mid-session yet
```

Verdict is `FAIL`, not `CONDITIONAL`: the responsive gate and the visual
deliverable are both unmet.

## The blocker from the previous run is closed

An Account Session could not reach `/api/account-context` or any Wagle route
while Markpoint required one — no single credential worked. Fixed minimally:
`get_current_user` accepts `role == "account"`, and `resolve_current_account`
(the **single** consumer of the `user` dict across all 16 routes) resolves an
Account token after checking its Session is live. **No router, schema,
migration or business rule changed**, and the legacy token still works.

## Defects I introduced and fixed

`/family` was a dead end for a multi-family account: `AccessBoundary` refused
whenever no family was active, and the screen it refused to show *was* the
selector. Journey 1 caught it. `/family` now renders its own selector and the
boundary links to it.

## Next agent first action

Three bounded follow-ups, none requiring the integration to be redone:

1. **Responsive** — 10 journey failures on iphone/ipad/android. The Wagle room list and the admin table are the two surfaces involved.
2. **Retire the legacy-premise suites** — `01-shell` and `02-wagle-realtime` assert a legacy session rendering preview fixtures. Rewriting them against the Account session is the correct fix; restoring the fixtures is not.
3. **Visual deliverable** — capture the 14 screens at both viewports with a manifest, and obtain a PM reference to compare against.

## Risks

- Do not restore the Wagle preview fixtures to make the 51 tests green.
- Do not narrow the auth bridge to Wagle only — `account-context` needs it too, and it is what supplies `activeFamilyId` to every screen.
- The frontend permission gates are UX only; every screen re-checks server-side.

## Forbidden Scope

Wave 7 cutover, legacy data deletion or backfill, Cheer/Feedback/Notification
implementation or retirement, and any
`reset`/`restore`/`checkout`/`clean`/`stash`/`commit`/`push`/`merge`/`rebase`/`PR`.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001.md`
- Independent QA: `blocked`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: the Wave 6 matrix is not passing; a coverage row now would overstate it.
- CLOSEOUT GATE: `BLOCKED`
- CLOSEOUT GATE Reason: responsive gate, visual deliverable and legacy-suite retirement outstanding.
