# Current Relay

Current Task: none — Wave 3 Core Lifecycle closed and graduated 2026-08-01
by PM final decision.

- PM verdict: `MONGLE-W3-FRONTEND-RUNTIME-CLOSEOUT-QA-001: PASS` /
  `WAVE_3_CORE_LIFECYCLE: COMPLETE` / `WAGLE_FRONTEND_CURRENT_SCOPE:
  INDEPENDENT_QA_PASS` / `WAVE_6_ROOM_UI_DEPENDENT_SCENARIOS:
  DEFERRED_WITH_EXPLICIT_ACCEPTANCE_CRITERIA` / `READY_FOR_WAVE_5: YES`.
- Graduated to `agent-system/graduated/2026-08.md`:
  `MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001`,
  `MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001`,
  `MONGLE-W3-WAGLE-INDEPENDENT-QA-001`,
  `MONGLE-W3-FRONTEND-RUNTIME-CLOSEOUT-QA-001`. Their handoffs moved to
  `agent-system/handoffs/archive/2026-08/`. Backlog rows for
  `MONGLE-W2-WAGLE-REALTIME-001` (Wave 3 scope), `MONGLE-W3-WAGLE-
  RECONNECT-RESUME-001`, `MONGLE-W3-WAGLE-MULTIFAMILY-SUBSCRIPTION-001`,
  `MONGLE-W3-WAGLE-FAILURE-ISOLATION-001`, `MONGLE-W3-WAGLE-PIN-LOCK-001`,
  `MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001` (foundational scope) marked `DONE`.
- Five browser-level realtime scenarios (ordinary reconnect, resume/missed-
  message recovery, duplicate-render prevention, sequence-gap refetch,
  per-Family-revoke UI isolation) plus a two-browser realtime journey were
  **not** opened as a new task (`MONGLE-W6-WAGLE-ROOM-REALTIME-UI-E2E-001`
  was explicitly declined by PM) — merged instead into
  `MONGLE-W5-TARGET-UI-001`'s existing Wave 6 DoD in
  `engineering/phase2/MONGLE_IMPLEMENTATION_BACKLOG.md`, to be proven once
  `WagleLanding` renders real rooms instead of preview fixtures. They are
  already independently verified at the Backend/API layer (239/239).
  Markpoint-route-unaffected-by-PIN-lock was added to the same DoD row,
  conditioned on a Markpoint frontend route existing (Wave 5 UI).
- D6-P1–P8 remain `DEFERRED_TO_RELEVANT_TASK_START_GATE`, untouched.

## Next Task

None claimed. Per PM's final status:

```text
WAVE_0..WAVE_4: COMPLETE
WAVE_3_CORE: COMPLETE
WAVE_5: READY_TO_START — MONGLE-W5-MARKPOINT-TARGET-OWNERSHIP-001 /
  MONGLE-W4-MARKPOINT-MISSION-LEDGER-001 (mission, ledger, level, reward on
  Target FamilyGroup/FamilyMembership ownership)
WAVE_6: NOT_STARTED
WAVE_7: NOT_STARTED
```

## Rules that stay in force

- **Anything new in the messaging domain is Wagle.** Naming gate was clean
  as of the last independent QA (0 live `doran` in frontend; 1 allowed
  prohibition comment in backend).
- **NOTIFY is a wake-up signal, never the message.** Identifiers only; the
  durable cursor catch-up must never be removed.
- **The Wagle device PIN must never** revoke a Session, silence Push, or
  block another service — schema-level guarantee, independently confirmed
  (no FK/status column from `wagle_device_pins` reaches `account_sessions`
  or `wagle_push_subscriptions`).
- Access = ACTIVE subscription AND ACTIVE membership AND no ACTIVE
  restriction. No `MarkpointParticipant` aggregate exists.
- FamilyAdmin is never automatically ServiceAdmin (migration `0006`).
- Wave 5 must land Target ownership **before** Markpoint product logic —
  never the reverse (per `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`'s own
  parallelization rule 4).

## Carried-forward items the next writer must not mistake for settled

- **`TRACEABILITY_GAP` remains** until PM commits: everything through Wave 4
  plus all of Wave 3 (backend, frontend, migration `0009`, this closeout's
  own governance edits) is uncommitted working state at `2243aa8`.
- **`docker-compose.phase2.yml` still does not exist** — the two-step
  disposable-DB setup (`database/init.sql` + `alembic upgrade head`) is done
  by hand every session.
- **9 documented-but-unregistered tasks** remain unregistered by PM decision.
- **Undocumented external worktree** under `/private/tmp/claude-501/...` —
  Human Gate under `DEC-2026-005`; not touched.
- **`PHASE0-AUTOMATED-GAP-CLOSEOUT-001`** is still `SUSPENDED` with measured
  authorization defects in the legacy mission/daily-point/notification
  routes; untouched by Waves 2-4.
- **`MONGLE-W1-INDEPENDENT-QA-001`/`MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001`**
  remain `IN_PROGRESS` in `active.md`, evidence-complete but not yet
  PM-graduated — a separate, still-open decision from today's Wave 3
  graduation.

## Worktree state

HEAD `2243aa8` at the start of every task in this bundle; PM has now
directed a commit to close the traceability gap (see the commit this
governance session is about to make). Branch `dev-newmarkp`. Nothing
belonging to another task was reset, restored, cleaned or stashed. All QA
Docker containers/volumes/networks (disposable Postgres, cross-process
fan-out harness, `--workers 2` runtime check, `mc_phase1` Playwright stack)
were torn down at their own teardown — zero residue confirmed after each.
