# Current Relay

## MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-CONDITIONAL-CLOSEOUT-REMEDIATION-001 (remediation writer, current)

- Intended edits: `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_
  INTEGRATION_AUDIT_MATRIX.csv` (additive columns
  `Remediation_Evidence`/`Remediation_Note`/`Final_Classification`/
  `Final_Confidence`/`Implementation_Readiness` only, plus 1 plain
  data-entry fix to `Preview_Route` for `2o`/`3b` — original
  `Primary_Classification`/`Confidence` columns untouched);
  `..._REPORT.md` (append-only "Remediation Addendum" section, original
  report body untouched); this task's own new handoff/QA evidence;
  `agent-system/active.md` (new entry for this task, plus the parent
  audit entry's own `Next Action` line updated to point here — its own
  substantive Verification findings text left untouched); this relay.
- Scope: remediation of the parent audit's `CONDITIONAL` verdict — resolve
  all 11 `LOW`-confidence rows via fresh code evidence, verify
  `POLICY_BLOCKED`/`INFRASTRUCTURE_BLOCKED` grounds, sub-classify frozen-
  design actionability, build a PM Decision Docket + Implementation
  Readiness axis + proposed (non-started) Wave A–F grouping. No product/
  test/migration/seed edit, no route wiring, no canonical migration, no
  legacy removal, no CSS/design-asset edit, no API/store wiring, no
  common-component extraction, no W7.6 start, no test skip/disable.
- Protected: the parent audit task's own handoff/QA-evidence files (not
  touched, write-once); every product source file read (read-only); the
  W7.5 closeout's own handoff; all other domains' files; pre-existing
  dirty work from prior tasks this session.
- Status: complete. LOW confidence 11 -> 0. 6 rows reclassified
  `CANONICAL_PREVIEW_ONLY` -> `LEGACY_LIVE_UI_ACTIVE` (AdminDashboard
  legacy-equivalent evidence). 5 rows confidence-only upgraded. 2 rows
  reclassified `POLICY_BLOCKED` -> `INFRASTRUCTURE_BLOCKED` (`2b`, `2v`).
  Final classification sum 64, final confidence HIGH 51/MEDIUM 13/LOW 0.
  New Implementation Readiness axis populated for all 64 rows, sum 64.
  12-item PM Decision Docket written, each with concrete options, none
  pre-resolved. Wave A–F proposal written, 0 Waves started. Verdict
  remains `CONDITIONAL` (open product/design/policy/infrastructure
  decisions surfaced, not resolved by this task — that is the correct
  outcome, not a shortfall). W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`. No commit/push/
  merge/rebase.

## MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001 (audit writer, current)

- Intended edits: new `engineering/phase2/MONGLE_W7_4_LIVE_CONSUMER_
  INTEGRATION_AUDIT_MATRIX.csv` and `..._REPORT.md`; this task's own new
  handoff/QA evidence; `agent-system/active.md` (new entry for this task,
  plus the existing `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001
  (REOPENED)` entry's own `Next Action` line updated to point here — its
  own substantive findings text left untouched); this relay.
- Scope: read-only classification of all 64 canonical Screens' actual
  live-product consumption. No route/component add/remove/rename, no CSS/
  token change, no package manifest change, no product/test/migration/seed
  edit.
- Protected: `frontend/src/App.tsx` and every product source file read
  (read-only); the W7.5 closeout's own handoff (not touched); all other
  domains' files; pre-existing dirty work from prior tasks this session.
- Status: complete. Verdict `CONDITIONAL`. Denominator 64 independently
  re-derived from current `App.tsx`. 64/64 matrix, 0 unclassified, 0
  duplicate. `/family`/`/markpoint`/`/wagle` re-confirmed
  `LEGACY_LIVE_UI_ACTIVE` for 1b/1c/1d, matching the W7.4 reopen exactly;
  several nested canonical Screens inside those same routes independently
  confirmed genuinely live. 8 Gap Groups (GAP-A..H) identified. 11/64 rows
  `LOW` confidence — not rounded up to `PASS`. W7.5 overall remains
  `CONDITIONAL`/`HUMAN_GATE`; W7.6 remains `BLOCKED`. No commit/push/
  merge/rebase.

## MONGLE-W7-5-CODE-DEFECT-HARDENING-CLOSEOUT-001 (governance closeout, current)

- Intended edits: `agent-system/active.md` (new `NATIVE-E2E-FIXED-
  RESOURCE-CONTENTION-GAP-001` entry under a new "NON-BLOCKING TEST
  INFRASTRUCTURE DEBT" section only — no existing entry rewritten), this
  task's own new handoff, `agent-system/graduated/2026-08.md` (new row for
  this closeout task itself, not the W7.5 umbrella), this relay.
  `agent-system/qa/COVERAGE_MAP.md` read and confirmed already correct
  (from the prior corroborating Independent QA pass), not re-touched.
- Scope: governance closeout only — declare the W7.5 code-defect/Hardening
  axis `CLOSED` based on already-existing independent QA evidence (Board-
  room race, migration 0021, admin bcrypt, Popular Posts SQL, Markpoint
  KST/UTC boundary, Playwright fixed runtime, native E2E launcher
  lifecycle — full evidence-chain table in this task's own handoff), and
  register the newly-found `NATIVE-E2E-FIXED-RESOURCE-CONTENTION-GAP-001`
  as separate, explicitly non-blocking test-infrastructure debt. No
  product/test/migration/seed edit; no new independent QA run performed by
  this task itself.
- Protected: every individual lineage task's own existing `active.md`
  entry (including their own prior append-only corrections) — read, not
  edited; the persistent local dev stack; all other domains' files.
- Status: complete. **W7.5 code-defect hardening: CLOSED.** W7.5 overall
  remains `CONDITIONAL`/`HUMAN_GATE` (PM/design decision gates,
  `GATE-2B` infrastructure decision, and W7.4's own reopened live-consumer-
  integration audit all remain open, untouched by this closeout). W7.4
  remains `REOPENED`; W7.6 remains `BLOCKED`.
- **Next authoritative task: `MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-
  AUDIT-001`** (not yet opened — this closeout only names it as the
  correct next axis, per its own brief; opening it is a separate action).
- **Deferred, non-blocking**: `NATIVE-E2E-FIXED-RESOURCE-CONTENTION-
  GAP-001` (test-infrastructure debt, `OPEN`/`MEDIUM`, unscheduled) — see
  its own `active.md` entry. Explicitly not a W7.5 code-defect and not a
  blocker for anything above.
- No commit/push/merge/rebase performed.

## MONGLE-W7-5-NATIVE-E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001 (independent QA, current)

- Intended QA artifact: create only `agent-system/qa/MONGLE-W7-5-NATIVE-
  E2E-LAUNCHER-FOCUSED-INDEPENDENT-QA-001.md`. Records current-HEAD
  (`328d877`) independent verification of the native launcher's own
  process-lifecycle contract via 2 real consecutive invocations. Product,
  test, migration, seed, and Playwright spec are protected — confirmed
  byte-identical to HEAD at both start and end.
- Runtime scope: native local PostgreSQL 16 disposable databases (fixed
  name `mc_w75_native_runner`, per the launcher's own default — created and
  dropped by the launcher itself across 2 runs), Node 20.20.2/Playwright
  1.58.2/Chromium v1208. **Disclosed collision**: a separate, concurrently-
  running Claude Code session independently invoked the same launcher with
  the same fixed DB name/ports during this exact window (see this task's
  own QA evidence Finding QA-F-001) — observed, not interfered with. This
  session's own separate persistent dev.sh stack (8000/5174) and any NAS/
  production system were excluded and confirmed untouched. No commit/push/
  merge/rebase/reset/clean/stash.
- Result: `CONDITIONAL` — `E2E-RUNTIME-F-001`'s own lifecycle contract
  independently verified held in both runs (Backend/Vite alive before and
  after Playwright in both the passing and failing run; cleanup only after
  Playwright; exit code preserved); the literal two-consecutive-clean-runs
  gate not yet achieved this pass due to the disclosed concurrent-session
  collision, not a reintroduced lifecycle defect.
- **Correction (append-only)**: the disclosed concurrent session was a
  second Independent QA session running this exact Task ID. That session's
  own corroborating pass (appended to this task's QA Evidence file)
  independently re-ran the same protocol twice after confirming no
  contention remained: two clean pairs, 4/4 runs 10/10. Revised result:
  `E2E-RUNTIME-F-001` lifecycle contract AND the two-consecutive-clean-runs
  gate both independently satisfied — code-defect-hardening scope CLOSED.
  W7.5 overall remains `CONDITIONAL`/`HUMAN_GATE`; W7.4 remains `REOPENED`;
  W7.6 remains `BLOCKED`.

## MONGLE-W7-5-NATIVE-E2E-LAUNCHER-LIFECYCLE-REMEDIATION-001 (developer, current)

- Intended/actual edits: new `tests/e2e/scripts/run-w75-full-spec-native.sh`
  (lifecycle-safe native equivalent of `run-w75-full-spec.sh`, reusing its
  own proven `( cd dir && exec ... ) & PID=$!` pattern verbatim plus extra
  `kill -0` liveness re-checks); `tests/README.md` (new documentation
  section); this task's own new handoff/QA evidence; `active.md`, this
  relay, `agent-system/qa/COVERAGE_MAP.md`.
- Scope: fix `E2E-RUNTIME-F-001` only — the native launcher's own process
  lifecycle. No product/backend/migration/seed/Playwright-spec/assertion
  change, no touching `run-w75-full-spec.sh` (Docker variant),
  `playwright.mongle-manual.config.ts`, or `tests/e2e/package.json`.
- Protected: the persistent local dev stack (`mc_festival`, this session's
  own separate `dev.sh`, ports 8000/5174); all other domains' files; the
  parent task's own FAIL record (kept, not rewritten).
- Status: lifecycle smoke PASS (24s hold, 3/3 checks clean); full native
  E2E run **10 passed / 0 failed / 0 skipped (53.9s)**, both service PIDs
  confirmed alive immediately before and immediately after Playwright;
  cleanup confirmed (QA DB/ports/log removed, persistent stack unaffected);
  static checks clean. No self-declared Independent QA PASS; awaiting a
  follow-up focused Independent Re-QA. No commit/push/merge/rebase.

## MONGLE-W7-5-E2E-PLAYWRIGHT-RUNTIME-REPRODUCIBILITY-CLOSEOUT-001 (developer, current)

- Intended edits: `tests/e2e/package.json` and its existing npm
  `package-lock.json` only to pin the already lock-resolved Playwright 1.58.2
  exactly; `tests/README.md` for the fixed local-runtime command; this task's
  new handoff/QA evidence, `active.md`, this relay, and Coverage Map only when
  execution status changes. No `pnpm-workspace.yaml` exists; frontend's
  pre-existing pnpm migration files are protected and out of scope.
- Scope: eliminate E2E's interactive latest-install path, install Chromium
  through the locked local package into an ignored in-worktree location, then
  perform one isolated native PostgreSQL + current-worktree Backend + Vite +
  Chromium run of the unchanged 10-test spec. Runtime artifacts remain under
  ignored `tests/e2e/.runtime/`; persistent 5432/8000/5173 is protected.
- Protected: product, migration, seed, E2E spec/assertions/config semantics,
  existing dirty work and all other task records. No commit/push/merge/rebase,
  global package install, latest/dlx/npx install, retry/skip/timeout change.
- Status: Node 20.20.2 fixed local runtime and Chromium v1208/headless-shell
  launch passed. The unchanged spec executed 10 failed / 0 passed / 0 skipped
  because the task-owned temporary launcher released QA Backend/Vite after
  readiness (`E2E-RUNTIME-F-001`). No retry or product edit; QA resources
  removed and persistent dev stack untouched.

## MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-FOCUSED-INDEPENDENT-RE-QA-001 (independent QA, current)

- Intended edits: only this task's new QA evidence and active handoff, then
  `agent-system/active.md`, this relay, and `agent-system/qa/COVERAGE_MAP.md`
  if the independently measured verification/environment status changes.
  Runtime artifacts are limited to the existing ignored
  `tests/e2e/.runtime/non-docker-closeout/` path and are removed on cleanup.
- Scope: independently verify the remediation task's correction lineage,
  seven-file commit boundary, new deducted-side deterministic test, the two
  KST-anchor tests under three OS timezones, the Markpoint suite, backend
  full-suite gate twice consecutively, one Docker E2E smoke, runner-induced
  Git delta, and start/end baselines. Migration 0021, board-room 5×10, and
  four-run runner history are explicitly excluded unless the current diff
  reaches their files.
- Protected: all product, test, migration, seed, Compose, and persistent-dev
  runtime files; pre-existing dirty files listed by the start baseline. No
  commit/push/merge/rebase/reset/clean/stash.
- Status: suspended after continuation under explicit PM/architect direction
  attempted to prove
  a non-Docker equivalent: isolated native PostgreSQL + current-worktree
  uvicorn + Vite + the runner's same manual Playwright config/spec/Chromium.
  The persistent 5432/8000/5173 dev stack is protected. Independent checks pass:
  exact 7-file `328d877` scope and append-only correction lineage; deducted
  test; three TZ runs; Markpoint suite 64/64; backend 405/405 twice on the
  same fresh disposable DB. `docker` remains absent in this WSL environment,
  so E2E is `ENVIRONMENT_REQUIRED`, never PASS. The final-E2E continuation
  re-confirmed that absence before invocation; static runner checks are clean.
  QA DB and in-worktree runtime artifacts were removed; start/end Git baseline
  has no runner-induced delta. Native DB + uvicorn + pnpm/Vite readiness was
  proven, but identical spec execution stopped before Chromium because the
  fixed `tests/e2e` Playwright runtime is absent; no latest-package install was
  accepted. Task-owned resources were removed.

## MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001 (implementation writer, current)

- Intended/actual edits: `backend/tests/test_markpoint_core_gap_wave5.py`
  (2 anchor-line replacements in pre-existing tests, `date.today()` ->
  `datetime.now(service.KST).date()`, zero assertion change; +1 new
  deterministic test for the deducted-side KST boundary), `agent-system/qa/
  MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md` and its
  handoff (append-only `## Correction` sections re: commit/push staleness,
  originals preserved), new `agent-system/handoffs/active/MONGLE-W7-5-
  MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md` and `agent-system/qa/
  MONGLE-W7-5-MARKPOINT-CONDITIONAL-CLOSEOUT-REMEDIATION-001.md` (this
  task's own records), `agent-system/qa/COVERAGE_MAP.md`, `active.md`, this
  file.
- Scope: dispose of `QA-F-001`/`QA-F-002`/`QA-F-003` from `MONGLE-W7-5-
  MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001`'s own `CONDITIONAL`
  verdict, and attempt the E2E smoke it also named as outstanding. No new
  feature work, no product-code change (out of scope — already verified
  correct), no touching `test_projection_reflects_a_reversal`'s own
  similarly-shaped `date.today()` (never flagged by the parent QA task,
  out of PM's named scope).
- Protected: `backend/app/domains/markpoint_target/service.py` (untouched);
  all other domains' files; the persistent local dev stack
  (`mc_festival`, this session's own separate `dev.sh`), observed/used only
  for unrelated manual UI testing earlier this session, never a mutation
  target here.
- Status: scopes 1/2/3/4/6 complete — commit-scope re-audit clean (7 files);
  both documentation corrections appended; new deducted-side test 3/3
  consecutive; the two fixed tests re-verified passing under
  `TZ=Asia/Seoul`/`TZ=UTC`/`TZ=America/New_York` (previously 1/3 under
  `America/New_York`); Backend full suite two consecutive runs, same
  disposable DB, **405/405 both runs**, 0 task-owned failure. Scope 5 (E2E
  smoke) NOT performed — this session has no Docker either; recorded
  `ENVIRONMENT_REQUIRED`, not PASS, per PM's own explicit instruction not to
  treat the WSL constraint as a substitute. No self-declared Independent QA
  PASS; awaiting a focused Independent Re-QA. No commit/push/merge/rebase.

## MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001 (independent QA, current)

- Intended QA artifact: create only `agent-system/qa/MONGLE-W7-5-MARKPOINT-
  PROJECTION-FOCUSED-INDEPENDENT-QA-001.md`. Records current-HEAD
  (`328d877`), disposable-environment evidence for `RE-QA-F-003`'s
  remediation: root-cause re-derivation, both originally-failing tests x5,
  the 5 new deterministic tests, a combined 124-test Markpoint-adjacent
  suite, OS-process-timezone and DB-session-timezone cross-checks, Hardening
  backend smoke, and two independent full-backend-suite runs. Product, test,
  migration, and seed files are protected — confirmed byte-identical to HEAD
  at both start and end. `CONDITIONAL` verdict, not `PASS`: 3 findings
  disclosed (commit/push documentation staleness; a deducted-side test
  coverage gap in the 5 committed regression tests, independently closed as
  correct-but-untested via a throwaway QA diagnostic; pre-existing OS-
  timezone fragility in the two originally-failing tests' own `date.today()`
  anchor) plus the E2E Playwright runner smoke being un-runnable in this
  session's own Docker-less WSL environment (`ENVIRONMENT_REQUIRED`).
- Runtime scope: a native local PostgreSQL 16 disposable database
  (`mc_qa_markpoint_verify`; no Docker available this session), created and
  dropped within this task only. This session's own separate persistent
  local dev stack (`mc_festival`, unrelated `dev.sh` work) and any NAS/
  production system were excluded and confirmed untouched. No commit/push/
  merge/rebase/reset/clean/stash.

## MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001 (implementation writer, current)

- Intended/actual edits: `backend/app/domains/markpoint_target/service.py`
  (`KST`/`_today_kst()` added, all 7 `date.today()` call sites replaced,
  `_sum_ledger`/`own_summary`'s ledger day-boundary SQL converted to KST
  before date extraction), `backend/tests/test_markpoint_core_gap_wave5.py`
  (+5 deterministic regression tests), new
  `agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`
  and `agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`,
  `agent-system/qa/COVERAGE_MAP.md`, `active.md`, this file.
- Scope: fix `RE-QA-F-003` from
  `agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001.md`
  only. No assertion/expected-value change, no touching the
  Migration-0021/E2E-runner lineage beyond a non-modifying smoke re-run, no
  touching the concurrently-active W7.4 REOPENED scope.
- Protected: the persistent dev runtime; legacy `mission`/`mission_template`/
  `config` domains (naive `date.today()` there is out of this task's scope,
  and `mission_template`'s rolling-window day-count contract is a
  separately PM-locked concern); all other domains' files.
- Status: all required steps complete — reproduction matrix classified
  `DATE_TIMEZONE_BOUNDARY_DEFECT` by direct measurement, fix applied and
  regression-tested (5 new deterministic tests), focused tests 5/5
  consecutive, backend suite 404/404 twice (one Wagle known-condition
  failure on Run 1 confirmed pre-existing and unrelated via standalone
  re-run), Hardening-lineage smoke clean, E2E runner 1x clean, static
  checks clean. No self-declared Independent QA PASS; awaiting follow-up.
  No commit/push/merge/rebase.

## MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001 (independent QA, current)

- Intended QA artifact: create only
  `agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001.md`.
  It records current-HEAD evidence for remediation of migration participant
  semantics and E2E repository-boundary compliance, plus the reproducible
  backend-suite gate failure. Product, test, migration, seed, and existing
  dirty files are protected; no status claim is predeclared.

## MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001 (implementation writer, current)

- Intended/actual edits: `backend/alembic/versions/0021_board_room_race_hardening.py`
  (participant-survivor algorithm rewrite + read-state sequence
  translation, per `HARDENING-QA-F-001`), new
  `backend/tests/test_migration_0021_participant_merge.py` (10-case
  regression matrix), `tests/e2e/scripts/run-w75-full-spec.sh` (log path
  moved off `/tmp` into an in-worktree runtime dir, per `HARDENING-QA-
  F-002`, plus a readiness-check hardening fix found while verifying that
  change), `tests/README.md`, root `.gitignore` (+`tests/e2e/.runtime/`),
  new `agent-system/handoffs/active/MONGLE-W7-5-HARDENING-QA-FAIL-
  REMEDIATION-001.md` and `agent-system/qa/MONGLE-W7-5-HARDENING-QA-FAIL-
  REMEDIATION-001.md` (this task's own dedicated records — sharing the
  parent task's files was not representable in `check_closeout.py`'s
  one-Task-ID-per-document model), plus a governance-format fix to the
  parent task's own
  `agent-system/handoffs/active/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`
  and `agent-system/qa/MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001.md`
  (added real `- Task ID:` list items and converted the Closeout
  Synchronization block to list-item fields — `check_closeout.py` was
  silently unable to recognize either document under its prior prose/
  code-fence formatting). `active.md` and this file updated.
- Scope: fix `HARDENING-QA-F-001` (HIGH) and `HARDENING-QA-F-002` (MEDIUM)
  from `agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001.md`
  only. No new feature work, no touching the concurrently-active
  `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)` scope, no
  touching the Independent QA session's own report above.
- Protected: the persistent dev runtime; all other domains' files; the
  REOPENED W7.4 task's own files/sections; the Independent QA report's own
  content (read, never edited).
- Status: all 9 scope steps complete — 10/10 migration regression cases
  pass, 4/4 consecutive E2E runner runs clean, 399/399 backend suite twice
  consecutively, Wagle 3x3 clean, static checks clean,
  `check_all.py` shows 0 warnings for either of this lineage's two Task
  IDs. No self-declared Independent QA PASS; awaiting
  `MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-RE-QA-001`. No commit/push/
  merge/rebase.

## MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001 (independent QA, current)

- Intended QA artifact: create/update only
  `agent-system/qa/MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001.md`
  with current-HEAD, disposable-environment evidence for migration 0021,
  board-room concurrency, legacy admin bcrypt, runner repeatability,
  artifact isolation, backend suite, focused tests, 3x3 regression, and
  static checks. Product, test, migration, seed, and existing dirty files
  are protected. `active.md`, this relay, the target hardening handoff, and
  Coverage Map will be read immediately before any required closeout-only
  synchronization; no status claim is predeclared.
- Runtime scope: dedicated disposable Docker/Postgres and temporary local
  backend/frontend processes only; persistent `mongle-*` runtime is
  excluded. No commit/push/merge/rebase/reset/clean/stash.

## MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001 (implementation writer, current)

- Intended/actual edits: `backend/app/domains/wagle/service.py` (GROUP
  `create_room` atomic get-or-create), `backend/app/domains/wagle/models.py`
  (mirrored unique-invariant `Index()` declaration), new
  `backend/alembic/versions/0021_board_room_race_hardening.py` (duplicate
  merge + unique constraint, real `downgrade()`),
  `backend/app/domains/auth/service.py` (legacy admin bcrypt 72-byte guard
  -- `auth/schema.py` was **not** touched; the fix is at the bcrypt call
  site, not input rejection), `backend/tests/test_wagle_integration.py`
  (+1 concurrency test), `backend/tests/test_auth_admin_login.py` (new, 6
  tests), `tests/e2e/scripts/run-w75-full-spec.sh` (Postgres readiness,
  removed `init.sql ... || true`), `tests/README.md`, root `.gitignore`
  (+`tests/e2e/test-results/`, and `git rm --cached` on the previously
  tracked `.last-run.json`, kept on disk), plus this task's own
  handoff/QA evidence, `agent-system/qa/COVERAGE_MAP.md`, `active.md`, and
  this file. **Status: all 13 scope steps complete** — see this task's own
  QA evidence Final Declaration.
- Scope: fix `RE-QA-F-BOARD-ROOM-RACE` (HIGH), `RE-QA-F-ADMIN-LOGIN-BCRYPT`
  (MEDIUM), `RE-QA-F-2T-RUNNER-FLAKY` (LOW) from
  `agent-system/qa/MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md`. No new
  product feature, no W7.6 common-component work, no touching the
  concurrently-active `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001
  (REOPENED)` scope in `active.md`.
- Protected: the persistent dev runtime (`mongle-db-1`/`mongle-backend-1`) —
  observed read-only only (confirmed 0 duplicate board rooms present as of
  this task's own start), never a test-mutation target; all other domains'
  files; the REOPENED W7.4 task's own files/sections.
- PM constraints: fixed step order, no per-step approval pause, except a
  HUMAN_GATE stop if a genuinely unmergeable duplicate-data conflict is
  found (none found — see this task's own handoff). Developer completion
  only; do not self-declare Independent QA PASS. No commit/push/merge/
  rebase.

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
- Phase I (2026-08-03, current, authoritative —
  MONGLE-W7-5-INDEPENDENT-QA-REMEDIATION-001): no commit/push/merge/rebase
  performed. **Disclosure**: `agent-system/qa/MONGLE-W7-5-INDEPENDENT-QA-
  001.md`, the report this remediation instruction named as its own
  evidence, does not exist in this repository, its git history, or any
  task registry — every technical claim below was independently
  reproduced against current source and a live disposable database, not
  trusted from that report. Modified: `backend/app/domains/wagle/
  service.py` (F1: `list_popular_posts`'s `range=week`/`month` 500 fixed,
  `:days * INTERVAL '1 day'` replacing an int-into-text-concat interval
  expression PostgreSQL has no operator for), `backend/tests/
  test_w75_phase_d_board_reactions.py` (+7 regression tests, proven real
  via revert-and-reconfirm), `tests/e2e/specs-mongle/
  04-w75-data-wiring.spec.ts` (F1 evidence-gap fix: real network-response
  assertion + overlay-scoped text replacing a page-wide text search that
  could pass on a 500; plus a `waitForLoadState('networkidle')` fix for a
  newly-found board-room creation race the stricter assertion surfaced),
  `frontend/src/platform/wagle/board/WagleBoardPage.tsx` (Popular Posts
  fetch-failure/empty-result conflation fixed), new
  `tests/e2e/scripts/run-w75-full-spec.sh` + `tests/README.md` update (F2:
  no-manual-steps runner for the full permanent spec including `2t`,
  verified 10/10 twice consecutively), `tests/e2e/test-results/
  .last-run.json` (F5: restored to HEAD via `git checkout --` after this
  checkpoint's own Playwright runs drifted it — recurs on every run,
  restored each time), plus `engineering/phase2/
  MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_REPORT.md` (§15),
  `agent-system/qa/MONGLE-W7-5-DATA-AND-BEHAVIOR-WIRING-001.md` (Phase I
  section), `agent-system/qa/COVERAGE_MAP.md`
  (`API-W7-5-BOARD-REACTIONS-001` 8/8→15/15, `E2E-W7-5-FULL-SPEC-001`
  F1/F2 notes), Handoff, and `active.md`. **F3**: full backend suite run
  twice consecutively post-fix — 382 passed (375 + 7 new tests), 0 failed,
  0 errors on run 1; see QA evidence for run 2's confirmed exact count.
  `KNOWN-W7-5-WAGLE-CONCURRENCY-001` remains registered, unaffected by
  this checkpoint. A genuinely new, unrelated defect (board-room race, see
  above) was found by this checkpoint's own stricter test assertions, not
  described in the original 4 findings — disclosed per this checkpoint's
  own Hallucination/Omission guards, fixed at the test level, with the
  underlying product-level race (real concurrent multi-device first-visit
  only) disclosed to PM as out of this checkpoint's no-new-migration
  scope. Unrelated concurrent work observed in the same worktree
  (a branding change touching 6 frontend files, `BrandCharacter` component
  + `aria-hidden` additions) — recorded, not touched. **Verdict:
  `REMEDIATION_EVIDENCE_FROZEN` / `READY_FOR_FOCUSED_INDEPENDENT_RE_QA`**
  — never `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS` or
  `MONGLE_W7_5_INDEPENDENT_QA_PASS`. All throwaway infrastructure used
  this checkpoint torn down and verified via `docker ps -a`/`lsof` after
  every run.
- Phase J (2026-08-03, current, authoritative —
  `MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001`, independent QA role, not
  the implementer): no commit/push/merge/rebase, no product/test/
  migration/seed code changed (SHA-256-verified against this pass's own
  start-of-session manifest). New files only: `agent-system/qa/
  MONGLE-W7-5-INDEPENDENT-QA-001.md` (recovered artifact — the originally
  cited Independent QA report never existed anywhere in this repository
  or its git history; recovered and explicitly labeled `RECOVERED_FROM_
  REPORTED_INDEPENDENT_QA_RESULT`) and `agent-system/qa/
  MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001.md` (this pass's own findings).
  **Verdict: `FAIL`** — the board-room duplicate-creation race Phase I
  disclosed as a test-level workaround is confirmed a genuine `PRODUCT_
  DEFECT` by real concurrency reproduction (5 concurrent requests × 10
  iterations against a fresh disposable DB, 10/10 iterations produced
  duplicate rooms, most with all 5 requests each creating a separate
  room — `wagle_rooms` has no unique constraint on `(family_group_id,
  title)` and `create_room`'s GROUP-room branch has no existing-room
  lookup or `IntegrityError` handling, unlike its own DIRECT-room branch).
  Per this task's own governing instruction, this blocks W7.6 until
  fixed. Independently re-verified clean otherwise: F1's fix (code audit
  + fresh isolated-stack reproduction of week/month/all/default/invalid/
  cross-family/period/sort/aggregation, all correct) and its 7 new tests
  (15/15, audited to assert real DB state not status-codes-only), the
  Playwright stale-DOM evidence-gap fix (confirmed structurally
  incapable of a false positive by direct code read), 2 more independent
  consecutive clean backend-suite runs (382/382 both, test count
  independently collected not assumed), and a freshly-written 3×3 Wagle
  viewport regression (9/9 checks clean). 2 new findings beyond Phase
  I's declared scope: the F2 runner (`run-w75-full-spec.sh`) failed 2 of
  4 independent back-to-back invocations on disposable-Postgres-
  readiness timing (root cause: `database/init.sql`'s load result is
  swallowed by `|| true`); and `backend/app/domains/auth/service.py::
  authenticate_admin` (legacy admin login, fully unauthenticated) has
  the same unfixed bcrypt-72-byte-limit defect class Phase H fixed in
  `service_actor.py` — reproduced a real 500 with a 153-byte password
  against the seeded `dad` account.
- PM correction (2026-08-03, same day, official status update — not a
  Phase J finding, a separate governance decision): `MONGLE-W7-4-
  PRODUCT-STRUCTURE-INTEGRATION-001` is **`REOPENED`** from `graduated/
  2026-08.md` with status `SCOPE_AND_EVIDENCE_DEFECT` —
  `LIVE_CONSUMER_INTEGRATION_COVERAGE: UNKNOWN`,
  `CONFIRMED_CANONICAL_RESKIN_MISSING: 1b, 1c, 1d`. Found in an unrelated
  W7.5 QA conversation: `frontend/src/App.tsx`'s own existing code
  comment already discloses that `/family`, `/markpoint`, `/wagle` are
  pre-existing functional pages "used as-is, not reskinned to the W7.3
  canonical mockups" for `1b`/`1c`/`1d` respectively (mockups reachable
  at `/__wave6/1b`, `/__wave6/1c`, `/__wave6/1d`) — W7.4's own self-
  reported "64/64 `PRODUCT_STRUCTURE_INTEGRATED`" conflated "route
  resolves to some page" with "route resolves to that Screen's own
  canonical design" for these 3. See `agent-system/active.md`'s own
  `MONGLE-W7-4-PRODUCT-STRUCTURE-INTEGRATION-001 (REOPENED)` entry and
  the corresponding correction note appended to `graduated/2026-08.md`'s
  original W7.4 row (write-once — the original row is kept, not
  rewritten). W7.5's own feature/defect verification to date is not
  retracted by this correction, but final functional completion of these
  3 canonical main screens is now recorded as unverified. Combined
  `W7_6_READINESS: BLOCKED` (board-room race + legacy-admin bcrypt +
  this reopened scope question, all pending resolution before any W7.6
  common-component extraction work begins).

## MONGLE-W7-2-REMAINING-REACT-CANONICAL-PORT-001 (implementation writer)

- Intended edits: new owner-local detached canonical screen/fixture/CSS files for the Matrix-filtered W7.2 rows, minimal `/__wave6/*` imports/routes in `frontend/src/App.tsx`, and this task's report/matrix/handoff/QA/active/relay records.
- Scope: 28 `W7_2_PORT_READY=YES` labels only; detached presentation, local CSS Modules, typed fixtures, and responsive internal layout. No active product route, dashboard mount, API/store/storage/WebSocket, Shared extraction, backend, package, or configuration work.
- Protected: all start-dirty paths other than task-owned App route additions; all existing 36 canonical previews and all product routes.

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
