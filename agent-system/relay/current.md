# Current Relay

Current Task: none — 1c mobile visual and source-separation closeout complete.

- Closed: A1 and 1c mobile visual/source separation. 1c preserved visual,
  behavioral and network identity across 375/390/430 after page-local colocation.
- Next: 1e admin sample canonical measurement only — confirm PNG/HTML authority,
  desktop capture contract, sidebar/header/table/action density and existing-admin
  comparison before any 1e implementation. Tablet remains not started.

- **Wave 5 Markpoint Core is complete and independently verified.** Coverage
  Matrix: `COVERED_TARGET 10` / Core `PARTIALLY_COVERED 0` /
  `MISSING_REQUIRED_IN_WAVE_5 0` / `UNCLASSIFIED 0`. Independent QA found
  **0 product defects**; its only `CONDITIONAL` cause was two stale docstrings,
  now corrected by `MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001`.
- Graduated: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001`,
  `MONGLE-W5-MARKPOINT-FUNCTIONAL-COVERAGE-GAP-COMPLETION-001`,
  `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`,
  `MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001`,
  `MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001`.
- Effective Wave 5 verdict: **PASS after the required documentation
  correction.** The independent QA's own `CONDITIONAL` is preserved verbatim in
  its report and deliberately not rewritten — the record that the gap existed
  and was found is worth more than a tidy verdict line.

## Two record defects, corrected — PM-dispositioned 2026-08-01

```text
Concurrent writer claim coexistence : RESOLVED_PROCESS_INCIDENT
Markdown header splice corruption   : RESOLVED_PROCESS_INCIDENT
Product impact                      : NONE
Lifecycle impact                    : NONE
```

Recorded rather than quietly repaired, because both are the shape the record
audit exists to catch and both were mine. PM approved keeping the occurrence,
cause, recovery and prevention rule on the record instead of deleting them:

1. **This file briefly carried two writer claims** — the record-integrity audit
   claimed the top while the Wave 5 writer claimed the `Current Task` section,
   because the two ran concurrently. `rules.md` treats the relay as the
   single-writer register, so that is a genuine defect. Neither writer's content
   was lost.
2. **A naive string splice mangled this file's header.** An edit that searched
   for the `Current Task` heading matched an *earlier quoted mention* of the
   same words inside a sentence and cut there, truncating the audit's own note
   mid-clause. Fixed by rewriting the header. **Standing rule, PM-retained:
   when splicing Markdown by heading, anchor on the line start, never on the
   words** — a quoted mention of a heading inside prose will match first.

## BG-1 credential-surface gap — correction re-verified, full-suite gate remains (2026-08-01)

`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001`'s `BLOCKED` finding (no single
credential reached both the family/Wagle API and the Markpoint Target API)
was addressed by `MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001`: a pre-existing
but uncommitted/unregistered fix was found, re-measured live, then
root-cause corrected — its Account-branch had duplicated
`get_current_account`'s Session-liveness check verbatim; both entry points
now share one function, `auth_service.resolve_account_from_session_claim`.

**Independent QA ran and returned `BLOCKED`**
(`MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001`): a
validly-signed Account token with a non-numeric `sid` escaped the auth
contract as an unhandled `ValueError` (500) instead of 401. This is the
system working as intended — an independent QA that reproduces from
scratch and attacks the boundary instead of re-reading the self-check
report. Fixed with the same guard pattern already used for `sub`; a
regression test was added and confirmed (via `git stash`) to fail pre-fix
and pass post-fix. The correction was then independently rechecked on two
separately initialized disposable databases: the six targeted HTTP tests
passed twice and independently crafted malformed claim variants all failed
closed with 401. A fresh full-suite run did not complete (it remained running
after 32 tests and was deliberately stopped), so BG-1 remains **CONDITIONAL**
until a complete independent full regression is recorded. The role widening,
shared resolver, and 38-usage enumeration remain separately evidenced.

## Next Task

**Complete an uncontended independent full-backend regression for
`MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001`**, then
**`MONGLE-W6-TARGET-UI-START-REVIEW`** — Wave 6 Target UI Start Review.

## Markpoint rules the next writer must not undo

- **The Ledger is append-only and the database enforces it** —
  `markpoint_ledger_no_update` / `markpoint_ledger_no_delete`. A correction is a
  reversal plus an optional replacement, never an edit. Found by a test of mine
  being refused, which is the guard working.
- **Cycle config is per Family, not the legacy global `configs` row.** One
  Family's change must never move another's period boundaries.
- **No force override on Guard A or Guard B.** None is defined by contract, and
  an override is exactly where a guard quietly stops meaning anything.
- **Level input is `lifetime_earned`, never `current_balance`** — using the
  balance would drop a child's level the moment they spend points.
- **Bulk approval is all-or-nothing.** No approved contract defines partial
  success; adding per-item results is a contract change, not an improvement.
- **Rolling window: the code wins over its own docstring.**
  `get_rolling_window` gives a Monday 14 days while its docstring claims 7
  ("이번 주만"). The code is preserved. Do not "fix" it to match the prose
  without PM approval — it changes how many missions every Monday generates.
- **`markpoint.missions.manage` ≠ FamilyAdmin.** A family owner is refused every
  admin capability, and the HTTP matrix asserts it.

## Wave status

```text
WAVE_0..WAVE_5: COMPLETE   (Wave 5 graduated 2026-08-01)
WAVE_6: READY_TO_START — Target UI (MP-U01), the browser-level Markpoint
  journey, and the Cheer / Feedback / in-app Notification product decisions
  (MP-S01..S03), which remain PM_DECISION_REQUIRED and were never retired
  or reclassified
WAVE_7: NOT_STARTED — cutover, including retirement of the legacy
  `configs.point_cycle` row that Markpoint Target no longer reads
```

Wave 5 effective verdict: **EFFECTIVE_PASS_AFTER_DOCUMENTATION_CORRECTION**.
The independent QA's `CONDITIONAL` stands verbatim in its own report; it was a
documentation-freshness gate, not a product defect (Core defects: 0).

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

## Approved documentation-hygiene item (PM 2026-08-01)

```text
STALE_TEST_DOCSTRING : NON_BLOCKING_DOCUMENTATION_HYGIENE
WAVE_5_REOPEN        : NO
WAVE_6_START_BLOCK   : NO
```

`backend/tests/test_markpoint_core_gap_wave5.py::test_rolling_window_preserves_the_implemented_legacy_behaviour`
still carries a name and docstring describing the rolling-window contradiction
as unresolved. Its **assertions are correct and the product is unaffected** —
this is prose that outlived its context.

`MONGLE-W5-ROLLING-WINDOW-DOC-CLOSEOUT-001` was explicitly forbidden from
modifying test files, so leaving it was the right call there, and PM has
confirmed that. The next session **holding test-documentation authority**
applies it:

```text
rename to : test_rolling_window_uses_today_through_next_week_sunday_inclusive
docstring : restate the approved contract
            TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE
            (Monday 14 / Saturday 9 / Sunday 8 inclusive dates)
do NOT change: assertions, fixtures, or any other test
```

Recorded here rather than left in a report, because the whole point of the
closeout it came from is that stale prose beside correct code is how a settled
decision gets reversed by someone tidying up.

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
