# Current Relay

## MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001 (implementation writer, current)

- Intended edits: `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_MATRIX.csv`
  (new), `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_REPORT.md`
  (new), `agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md` (new),
  `agent-system/handoffs/active/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md`
  (new); `backend/app/domains/**` for existing-API reuse/extension or new
  vertical Slices as the Phase 0 Inventory identifies them; matching
  `frontend/src/**` adapter/ViewModel wiring for the 64 W7.4-bound canonical
  Screens; `backend/tests/**` and `tests/e2e/specs-mongle/**` for new
  coverage, following existing naming/config patterns (no new spec-naming
  convention exists yet — see this task's own Report for the documented
  conflict with `DEC-2026-004`'s reserved
  `MONGLE-TEST-SPEC-NAMING-CONVENTION-001`, resolved by following the
  already-used `test_<domain>_<feature>.py` pattern rather than blocking).
- Scope: wire the 64 canonical Screens W7.4 already bound into the product
  to real data/mutations/auth/error-state; reuse existing Backend/API first,
  extend minimally where partial, build new vertical Slices only where
  genuinely missing. No W7.3 visual-baseline change, no W7.4 route/topology
  rework, no policy-undecided feature (`3h` account deletion stays
  `POLICY_REQUIRED`/`HUMAN_GATE`).
- Protected: all W7.3/W7.4 frozen structure and baselines; all other domains'
  existing tests; the persistent dev runtime (`mongle-db-1`/`mongle-backend-1`)
  is observed only, never used as a test-mutation target this task —
  isolated `mc_phase0`/`mc_phase1` Compose stacks and disposable Postgres
  containers only, per `tests/README.md`.
- Registration/governance correction performed while opening this task (see
  `active.md` and `graduated/2026-08.md` for full detail): W7.3 and W7.4 were
  found completely unregistered despite real completed code; both are now
  graduated with disclosed self-check-only status, matching the existing
  `MONGLE-FE-ROUTE-NAMESPACE-MIGRATION-001` precedent. W7.4's QA evidence now
  carries an explicit `HISTORICAL_POLICY_DEVIATION` section (its verification
  used `/tmp` scripts and mutated the persistent dev DB rather than an
  isolated stack) — disclosed, not retroactively justified, and not treated
  as grounds to reverse its self-reported PASS.
- Phase D directory declaration (2026-08-03, per `CLAUDE.md`'s standing
  rule — these are new subdirectories under the existing, already-PM-
  approved `backend/app/domains/` extension point, not arbitrary top-level
  directories): `backend/app/domains/family_todo/`,
  `backend/app/domains/family_rules/`,
  `backend/app/domains/notification_preferences/`,
  `backend/app/domains/family_schedule/`,
  `backend/app/domains/family_album/`,
  `backend/app/domains/reward_catalog/`,
  `backend/app/domains/account_notification/`,
  `backend/app/domains/family_activity_log/`,
  `backend/app/domains/family_search/` — one per `SLICE-*` row in
  `engineering/phase2/MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md`. Built
  incrementally per that mapping's own execution order; not all may exist
  yet at any given read of this file — check the mapping doc and
  `active.md`'s own Phase D progress note for current state.
- Phase D checkpoint (2026-08-03): 10/11 backend Slices built, all 19
  candidate screens processed. Added 7 new migrations
  (`0013`→`0019`) and `backend/tests/test_w75_phase_d_slices.py` to the
  file set above; new domains under `backend/app/domains/` per the
  directory declaration further up this file. `2b`
  (`SLICE-WAGLE-ATTACHMENTS`) and `3e` (`SLICE-WAGLE-BOARD-REACTIONS`)
  remain unbuilt (policy/new-slice gated, not blocking). New
  `agent-system/qa/COVERAGE_MAP.md` row
  (`API-W7-5-PHASE-D-NEW-SLICES-001`); `KNOWN-W7-5-WAGLE-CONCURRENCY-001`
  updated with an 8th and 9th full-suite run's evidence. See `active.md`'s
  own entry and this task's Report §10-11 for the full per-Slice outcome,
  including the recurring missing-input-control finding across 6 screens
  (`1i`, `1v`, `2y`, `2z`, `3b`, `3j`) that now needs a PM/design decision.
- Phase C checkpoint (2026-08-03): 11/11 rows processed, added
  `backend/alembic/versions/0012_profile_mission_fields.py` and
  `backend/tests/test_w75_phase_c_extensions.py` to the file set above.
  `agent-system/qa/COVERAGE_MAP.md` updated with two new rows
  (`API-W7-5-PROFILE-MISSION-WAGLE-EXT-001`,
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001`). Now moving into Phase D — see
  `active.md`'s own entry for the full per-row outcome and this task's
  Report §9/§10.
- Phase E/F checkpoint (2026-08-03, current, supersedes the Phase D
  checkpoint above where they conflict): scope reconciliation +
  closeout-readiness pass, no commit/push/merge/rebase performed (per this
  checkpoint's own standing constraint). New file:
  `engineering/phase2/MONGLE_W7_5_PM_DECISION_PACKAGE.md`. Modified:
  `backend/app/domains/wagle/{models,schemas,service,router}.py`,
  `backend/app/domains/wagle/board_constants.py` (new),
  `backend/alembic/versions/0020_wagle_message_reactions.py` (new),
  `backend/tests/test_w75_phase_d_board_reactions.py` (new, 8/8 pass),
  `backend/scripts/phase1_seed_synthetic.py` (FK delete-order fix),
  `tests/e2e/specs-mongle/04-w75-data-wiring.spec.ts` (3c/3d/3e block
  added, then its own navigation defect fixed), six frontend
  fixture-fallback-on-error fixes (`FamilyMembersPage.tsx`,
  `FamilyTodoPage.tsx`, `FamilyRulesPage.tsx`, `FamilySchedulePage.tsx`,
  `FamilyAlbumPage.tsx`, `ProfilePage.tsx`),
  `frontend/src/platform/wagle/board/WagleBoardPage.tsx` (real reaction
  counts + real Popular Posts data), `frontend/src/shared/api/wagleApi.ts`
  (reaction/popular-posts client functions),
  `frontend/src/generated/openapi.d.ts` (regenerated),
  `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_MATRIX.csv`
  (`ORIGINAL_API_READINESS` column added, `3e`/`1f`/`2b` rows corrected),
  plus `agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md`,
  `agent-system/qa/COVERAGE_MAP.md`,
  `engineering/phase2/MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_REPORT.md` (§12
  added), this task's handoff, and `active.md`. `3e` resolved and built
  (not deferred — both its own and `3c`'s frozen Screens already render
  the `♥`/`💬` stat). 17 raw PM-gate screen flags reconciled to 13
  canonical gates (was miscounted "14" in `active.md`). Full backend
  suite: 374 passed, 1 pre-existing unrelated failure, 0 errors — cleanest
  run of the task. Permanent `3c/3d/3e` Playwright spec actually executed
  (not left as committed-but-unrun): first run failed on a real test
  defect (`page.goBack()` vs. `WagleBoardPage.tsx`'s component-state
  view), fixed; re-seeding exposed a second real defect in
  `phase1_seed_synthetic.py`'s delete ordering, fixed; re-run PASS 1/1.
  Verdict: `CONDITIONAL`/`HUMAN_GATE`, closeout-ready — 13 canonical PM
  gates plus `2b`'s own storage Decision Package are the only remaining
  open items, all requiring genuine PM/design decisions, none blocked on
  further code. Independent QA intentionally not started. Isolated test
  infrastructure (`mc_w75_r2_db` on 15435, backend on 18099, Vite on 5199)
  still running as of this checkpoint, pending final teardown after this
  pass's own verification completes.
- Phase G addendum (2026-08-03, same session): full `0012`→`0020`
  migration downgrade chain verified against a dedicated, separately
  torn-down throwaway DB (`mc_migration_verify`, port 15498 — never
  touched `mc_w75_r2_db`) — every migration's `downgrade()` is real, full
  round trip clean, 3 representative schema changes confirmed by direct
  inspection. Broadened frontend functional-state audit found and fixed 6
  more real defects across `FamilySchedulePage.tsx`, `FamilyTodoPage.tsx`,
  `FamilyAlbumPage.tsx`, `ProfilePage.tsx`, `WagleBoardPage.tsx`, plus a
  documentation-only comment update to `FamilySearchPage.tsx`. **Most
  significant finding**: `frontend/src/features/family-notifications/
  NotificationsPage.tsx` (`1n`) had never actually been wired to its own
  real backend despite being counted "Fully real end-to-end" in the Phase
  D checkpoint — corrected in the Handoff/Coverage Map in place, and the
  page is now genuinely wired (`shared/api/accountNotificationApi.ts`'s
  `listNotifications`/`markNotificationRead`/`markAllNotificationsRead`).
  `tsc --noEmit`/`eslint` clean. No scope/count change — `1n` was already
  counted as wired; only the truthfulness of that claim changed.
- Phase H (2026-08-03, current, authoritative — Final Pre-Independent-QA
  Reconciliation and Evidence Freeze): no commit/push/merge/rebase
  performed. Modified: `backend/app/domains/wagle/service_actor.py`
  (bcrypt 72-byte length-guard fix), `backend/app/domains/markpoint_target/
  service.py` (+`list_audit_events`, +`search_missions_by_title`),
  `backend/app/domains/wagle/service.py` (+`search_visible_messages`),
  `backend/app/domains/family_activity_log/service.py` and
  `backend/app/domains/family_search/service.py` (now call the above via
  dotted reference instead of querying other domains' models directly),
  `frontend/src/pages/profile/ProfilePage.tsx` (secondary-stat fixture-
  fallback fix), plus `engineering/phase2/MONGLE_W7_5_PM_DECISION_
  PACKAGE.md` (§4 rebuilt: 13 PM/design gates + `GATE-3E-REACTION-TOGGLE`
  added, `GATE-2B` moved to its own §4.2, 12-field-per-gate detail added),
  `agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md` (Phase H
  section), `agent-system/qa/COVERAGE_MAP.md` (`KNOWN-W7-5-WAGLE-
  CONCURRENCY-001` bcrypt-fix correction + 2 new runs, new
  `E2E-W7-5-FULL-SPEC-001` row), Report §14, Handoff, and `active.md`.
  Found and fixed: the "13 canonical gates" figure had itself wrongly
  folded in `GATE-2B` (an infrastructure question, not a product-policy
  one) — corrected to 13 PM/design + 1 infrastructure = 14 total; Phase
  D's "11/11 complete" phrasing self-contradicted "`2b` correctly not
  built" — corrected to `PHASE_D_TOTAL_SLICES_ORIGINAL_SCOPE=11`,
  `CODE-IMPLEMENTABLE_SLICES_COMPLETE=10/10`,
  `INFRASTRUCTURE-BLOCKED_SLICE=1`; the pre-existing `bcrypt` backend
  failure was root-caused and safely fixed (backend suite now genuinely
  375/375, re-verified twice); the Playwright `2t` skip was resolved
  (10/10, 0 skipped, synthetic disposable credential, same precedent as
  `2t`'s own Phase B API-level check); a genuine Backend Guide
  cross-domain-DB-access boundary gap was found and fixed (0 behavior
  change, 0 regressions); one more real frontend fixture-fallback defect
  (`ProfilePage.tsx`'s secondary stats) found and fixed; all 9 migrations
  cross-checked against their models, zero drift. Full verification suite
  clean: backend 375/375, E2E 10/10 (0 skipped), `tsc`/`eslint`/`vite
  build` clean, `agent-system/tools/check_all.py` shows no W7.5-specific
  warning, `git diff --check` clean. All throwaway infrastructure used
  this checkpoint (`mc_bcrypt_verify`, `mc_w75_r3_db`,
  `mc_guide_fix_verify`) torn down, zero residue. **Verdict:
  `IMPLEMENTATION_EVIDENCE_FROZEN` / `READY_FOR_PM_REVIEW` /
  `READY_FOR_INDEPENDENT_QA`** — never `MONGLE_W7_5_DATA_AND_BEHAVIOR_
  WIRING_PASS` or `INDEPENDENT_QA_PASS` while the 14 decision items remain
  genuinely open.

## MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001 (implementation writer)

- Intended edits: new owner-local detached canonical screen/fixture/CSS files for the Matrix-filtered W7.2 rows, minimal `/__wave6/*` imports/routes in `frontend/src/App.tsx`, and this task's report/matrix/handoff/QA/active/relay records.
- Scope: 28 `W7_2_PORT_READY=YES` labels only; detached presentation, local CSS Modules, typed fixtures, and responsive internal layout. No active product route, dashboard mount, API/store/storage/WebSocket, Shared extraction, backend, package, or configuration work.
- Protected: all start-dirty paths other than task-owned App route additions; all existing 36 canonical previews and all product routes.

## MONGLE-W7-1-SCREEN-OWNERSHIP-TOPOLOGY-FREEZE-001 (audit writer)

- Intended edits: `engineering/phase2/MONGLE_W7_SCREEN_OWNERSHIP_AND_TOPOLOGY_FREEZE.md`, `engineering/phase2/MONGLE_W7_SCREEN_OWNERSHIP_MATRIX.csv`, this task's handoff/QA record, and task registration state only.
- Scope: read-only ownership/topology classification from the Wave 7.0 authority report/matrix and current frontend source. No React, CSS, routes, files/directories, API, backend, package, runtime, or Docker changes.
- Protected: all existing dirty paths, including `frontend/src/App.tsx`, Wave 6 previews/evidence, and Wave 7.0 outputs.

Current Task: none — `MONGLE-W6-ALL-TOKENIZED-SCREENS-SEQUENTIAL-PORTING-001` implementation closeout is ready for independent review. See its active handoff and QA evidence.

- Intended edits: `frontend/src/pages/<ScreenName>/**`, minimal detached
  `/__wave6/*` entries in `frontend/src/App.tsx`, one screen-status inventory,
  and task handoff/QA/active records. Existing previews and active product
  routes are protected; no shared-component, API, backend, DB, package, or
  configuration work.
- Current evidence state: 1448×1086 crop/resize 0; runtime, font, API,
  WebSocket, storage, navigation, overflow and scrollbar checks passed.
  Local SHA-256 inventory and Drive metadata readback are complete. The raster
  decoder/ROI skeleton remains experimental and is not a Visual PASS basis.
- Protected: A1, 1c, `/dashboard`, `/admin/points`,
  `AdminDashboard/views/PointView/**`, Auth, Backend, DB, package/config, and
  architecture documents. No API/session/navigation wiring.
- Canonical contract: approved A5 PNG, full bounds `0,0,1448,1086`, no crop or
  resize; HTML `1e` is structure-only. This task stops at
  `READY_FOR_GPT_VISUAL_REVIEW` after evidence closeout.

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
