# Independent QA — MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001

```text
Task:    MONGLE-W7-5-MARKPOINT-PROJECTION-FOCUSED-INDEPENDENT-QA-001
Target:  MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001
Finding: RE-QA-F-003
Observed: 2026-08-04, branch dev-newmarkp, HEAD 328d877c162e300ffafbbc566a70d36bba4f3a2d
Verdict: CONDITIONAL
```

## Environment disclosure (read before anything else in this report)

This QA session ran in a **WSL environment with no Docker installed at all**
(`docker: command not found`). This differs from every prior QA pass on this
task family, which used disposable `postgres:16.9-alpine` Docker containers.
To still perform real, independent, isolated-DB verification:

- A native local PostgreSQL 16 cluster (already running on this host,
  port 5432) was used instead of a Docker container.
- A dedicated disposable database, `mc_qa_markpoint_verify`, was created for
  this task only (`database/init.sql` baseline + `alembic stamp
  0000_legacy_schema_baseline` + `alembic upgrade head` through `0021`),
  used exclusively by this QA pass, and dropped at the end. It never shared
  state with the persistent local dev stack (`mc_festival`, started earlier
  this session via this repo's own new `dev.sh` for unrelated manual UI
  testing) or with any NAS/production system.
- Consequence: **`tests/e2e/scripts/run-w75-full-spec.sh` (Playwright E2E
  runner) could not be executed** — it requires Docker to bring up its own
  disposable Postgres container. This is recorded as `ENVIRONMENT_REQUIRED`
  per `TEST_POLICY.md`'s BLOCKED taxonomy, not as a failure or a skipped
  PASS. The diff audit below independently confirms this remediation
  touched zero E2E-runner-related files, so this gap does not cast doubt on
  the remediation itself — it means one planned smoke check has no evidence
  either way in this environment.
- Everything else in this report (SQL-level mechanism reproduction, all
  Markpoint-suite pytest execution, both full-backend-suite runs, Hardening
  backend-only smoke, static checks) is real, independently executed
  evidence from this session, not carried forward from any prior report.

## Baseline

```text
worktree: /appl/point-festival
branch:   dev-newmarkp
HEAD:     328d877c162e300ffafbbc566a70d36bba4f3a2d (unchanged start -> end)
dirty (start == end, byte-identical, not touched by this QA pass):
  M  .gitignore
  D  frontend/package-lock.json
  M  frontend/vite.config.ts
  ?? dev.sh
  ?? frontend/pnpm-lock.yaml
  (all five predate this QA task -- this session's own earlier, unrelated
  native-dev-server setup work, tracked in this session's conversation, not
  part of MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001)
staged:    none
untracked: dev.sh, frontend/pnpm-lock.yaml (see above)
stash:     empty (git stash list: no output)
git diff --check: clean (exit 0), both start and end
```

**Disclosure superseding this task's own Section 5 instruction**: the
Developer's own QA Evidence and Handoff (read in full below) repeatedly and
explicitly state `No commit/push/merge/rebase performed`. That is
**contradicted by the actual repository state**: the fix is already
committed at the current HEAD (`328d877`, authored by `iamsonmac@gmail.com`,
message `fix(markpoint): correct KST/UTC date-boundary defect in Target
projection`, `Co-Authored-By: Claude Sonnet 5`) and is already reachable from
`origin/dev-newmarkp` (confirmed via `git branch -r --contains 328d877`).
This is recorded as an `EVIDENCE_GAP` / documentation-staleness finding
below (Finding QA-F-001) — most plausibly the PM committed and pushed after
the Developer wrote their records, and `active.md`/`relay/current.md` were
never updated to match. Per this task's own Gate 5 (Freshness), the rest of
this report verifies **current HEAD**, which already contains the fix, not
a hypothetical uncommitted working-tree diff.

No SHA-256 manifest file was separately generated; equivalent integrity
evidence was captured instead via direct `diff` between the committed HEAD
blob and the current working-tree file for both changed source files
(`backend/app/domains/markpoint_target/service.py`,
`backend/tests/test_markpoint_core_gap_wave5.py`) at both start and end of
this QA session — both byte-identical to HEAD both times, i.e. zero QA
modification.

## Root Cause Verification

```text
Reported classification:     DATE_TIMEZONE_BOUNDARY_DEFECT
Independent classification:  DATE_TIMEZONE_BOUNDARY_DEFECT (confirmed)
```

Verified independently, not re-read from the Developer's own trace, via a
direct raw-SQL experiment against the disposable QA database:

```sql
-- Same UTC instant (2026-08-03T15:30:00Z = 2026-08-04 00:30 KST) under two
-- DB session TimeZone settings:
SET TIME ZONE 'Asia/Seoul';
  OLD (pre-fix): date('...'::timestamptz)                              -> 2026-08-04
  NEW (fixed):   date(timezone('Asia/Seoul', '...'::timestamptz))      -> 2026-08-04
SET TIME ZONE 'UTC';
  OLD (pre-fix): date('...'::timestamptz)                              -> 2026-08-03  <- disagrees
  NEW (fixed):   date(timezone('Asia/Seoul', '...'::timestamptz))      -> 2026-08-04  <- unchanged
```

This directly reproduces the exact mechanism the Developer described,
independent of their own diagnostic script (which no longer exists — it was
deleted after use, per their own disclosure): the OLD expression's result
depends on the DB session's `TIMEZONE` GUC; the NEW expression is invariant
to it. `occurred_at`'s column type was independently confirmed as
`TIMESTAMP WITH TIME ZONE` (`information_schema.columns`), which is the
precondition for `timezone('Asia/Seoul', occurred_at)` to mean "convert this
absolute instant to KST wall-clock time" rather than the opposite
interpretation it would have on a naive column — confirmed correct, not
assumed.

```text
OS timezone behavior (product code):     INVARIANT post-fix (see below)
DB timezone behavior (product code):     INVARIANT post-fix (see below)
anchor behavior:                         _today_kst() uses datetime.now(KST)
                                          with an explicit ZoneInfo, never
                                          the ambient OS clock
previous symptom alignment:              today_earned/today_deducted -> 0,
                                          weekly_earned/weekly_deducted
                                          unaffected -- independently
                                          reproduced (see Date Boundary
                                          Evidence below); matches the
                                          Developer's own dump exactly
```

## Code Audit

```text
Files changed (git show --stat 328d877):
  backend/app/domains/markpoint_target/service.py     | 43 ++++-
  backend/tests/test_markpoint_core_gap_wave5.py       | 141 ++++++++++++++
  agent-system/active.md                               | 45 +++
  agent-system/relay/current.md                        | 28 +++
  agent-system/qa/COVERAGE_MAP.md                       | 3 +-
  agent-system/handoffs/active/...-001.md (new)         | 215 +++
  agent-system/qa/...-001.md (new)                      | 164 +++
  7 files changed, 628 insertions(+), 11 deletions(-)
```

- **KST helper**: `KST = ZoneInfo("Asia/Seoul")` + `_today_kst() ->
  datetime.now(KST).date()` added, reusing `daily_point/service.py`'s own
  established convention verbatim (same constant name, same construction) —
  independently confirmed by reading `daily_point/service.py`, not asserted
  from the commit message alone. No parallel, ad hoc timezone rule was
  invented.
- **`date.today()` removal**: independently grepped `markpoint_target/
  service.py` for `date.today(`, `datetime.today(`, `datetime.now(` — zero
  naive-clock call sites remain in that file; all 7 originally-reported call
  sites (`expire_stale_missions`, `own_summary`, `read_family_config`,
  `update_family_config`, `rolling_window`, `own_projection`,
  `own_weekly_detail`) now call `_today_kst()`, confirmed line-by-line
  against the actual diff, not the commit message's own claim.
- **Ledger SQL**: `_sum_ledger` and `own_summary`'s inline comparison both
  converted from `func.date(occurred_at)` (session-TZ-dependent) to
  `func.date(func.timezone("Asia/Seoul", occurred_at))`
  (session-TZ-independent, confirmed above). `_sum_ledger` compares the
  converted **date** with `>= start AND <= end` (both inclusive) — this is
  correct and not the lossy "23:59:59" pattern this task's own Section 10
  warns about, because the comparison operates on already-truncated
  **calendar dates**, not raw instants; there is no sub-day boundary left to
  lose. This is Option A from this task's own Section 10 ("occurred_at를
  KST로 변환한 뒤 날짜를 비교"), correctly implemented.
- **Range semantics**: unaffected; only which calendar date "today" resolves
  to changed, not how ranges are computed once dates are known.
- **Scope creep**: none found. `git diff` (via direct blob comparison, since
  `git diff <sha> <sha> -- <path>` produced empty output for this repository
  for reasons not further diagnosed — worked around via `git show
  <sha>:<path>` piped to `diff`, which did show correct content) confirms
  the product-code change is confined to `markpoint_target/service.py`.
  Independently confirmed via direct diff that `backend/app/domains/wagle/
  service.py`, `backend/app/domains/auth/service.py`, and
  `backend/alembic/versions/0021_board_room_race_hardening.py` are all
  **byte-identical** between this commit and its parent — zero touch, as
  reported.
- **Prohibited patterns**: none found. No assertion loosened (independently
  re-ran the two originally-failing tests against their own pre-existing
  assertions, unmodified — see below), no `skip`, no reordering, no
  sleep/retry, no test-only production branch, no global DB timezone
  override in product code (the fix converts explicitly at the query level,
  never issues `SET TIME ZONE`), no legacy `mission`/`mission_template`
  contract touched (independently confirmed those files are absent from the
  diff).

## Date Boundary Evidence

```text
KST timestamp:        2026-06-15 00:00:00+09 (MANUAL_DEBIT, amount=-18)
UTC timestamp:         2026-06-14 15:00:00+00
anchor date:            2026-06-15 (KST) vs 2026-06-14 (KST, adjacent day)
expected local date:    2026-06-15 (KST)
actual local date:      2026-06-15 (KST) -- confirmed via own_projection()
today_earned:            not applicable to this probe (deduction-only)
today_deducted:          18 (anchor=2026-06-15) / 0 (anchor=2026-06-14)
```

Produced by a standalone, throwaway QA diagnostic script (not committed, not
part of the test suite, deleted after use — same disclosed pattern the
Developer's own root-cause trace used) that reused this repository's own
existing `_family`/`_member` test fixtures from
`tests/test_markpoint_core_gap_wave5.py` (imported read-only, never edited)
to satisfy `own_projection`'s access-control precondition, then inserted one
`MANUAL_DEBIT` ledger row at a KST-midnight-crossing UTC instant and called
`own_projection` with two adjacent explicit KST anchors. Result matches
`today_earned`'s already-tested boundary behavior exactly, confirming the
fix is sign-agnostic (see Finding QA-F-002 below for why this had to be
checked independently).

## Regression Tests

### Existing failing tests × 5 (fresh disposable DB, no reset between runs)

```text
tests/test_markpoint_core_gap_wave5.py::test_projection_derives_every_figure_from_the_ledger
tests/test_markpoint_core_gap_wave5.py::test_projection_isolates_date_boundaries

Run 1: 2 passed, 3.48s
Run 2: 2 passed, 4.22s
Run 3: 2 passed, 3.28s
Run 4: 2 passed, 4.39s
Run 5: 2 passed, 4.12s
```

### New timezone regression tests (5/5)

| Test ID | Boundary time | Anchor | occurred_at | Expected date | Result |
| --- | --- | --- | --- | --- | --- |
| `test_projection_kst_boundary_independent_of_server_local_timezone` | 00:00 KST (= prior-day 15:00 UTC) | explicit `date(2026,3,11)` / `date(2026,3,10)` | explicit, constructed via `service.KST` | KST date, not UTC date | PASS |
| `test_projection_different_anchor_dates_isolate_correctly` | 12:00 KST, two distinct dates | explicit `date(2026,5,4)` / `date(2026,5,5)` | explicit | isolated per anchor | PASS |
| `test_projection_repeated_calls_same_db_return_identical_figures` | real "now" (no fixed boundary) | default (`_today_kst()`, real current KST date) | `server_default=func.now()` | idempotent across 2 calls | PASS |
| `test_projection_cross_family_isolation_for_today_earned` | 12:00 KST | explicit `date(2026,7,15)` | explicit | Family B sees 0 | PASS |
| `test_projection_empty_ledger_returns_zero_not_error` | n/a (no ledger rows) | explicit `date(2026,9,1)` | n/a | all-zero, no exception | PASS |

**Coverage gap disclosed (Finding QA-F-002)**: none of these 5 tests
constructs a **negative-amount** (`MANUAL_DEBIT`) ledger row at an explicit
KST/UTC boundary instant to directly assert `today_deducted`'s boundary
correctness the way `test_projection_kst_boundary_independent_of_server_
local_timezone` does for `today_earned`. Deducted-side boundary coverage
exists only via the pre-existing, non-deterministic
`test_projection_derives_every_figure_from_the_ledger` (uses real "now",
only actually exercises the boundary during the live ~9-hour daily
divergence window). This task's own Section 13 explicitly requires "earned
와 deducted 둘 다" in the deterministic set; that requirement is not met by
the 5 committed tests. Independently closed as a **coverage gap, not a
product defect** by the standalone diagnostic above (today_deducted correct
at the exact boundary), but the gap in the *committed, permanent* regression
suite remains real and is not self-closing.

### Markpoint-related suite (broader than the Developer's own 2-file, 63-test
scope — this QA additionally ran the 3 other Markpoin-adjacent files
discoverable in the repo)

```text
tests/test_markpoint_core_gap_wave5.py + test_markpoint_target_wave5.py:
  63 passed, 0 failed, 0 errors, 88.87s   (matches Developer's own 63 claim,
  independently reproduced, not copied)

tests/test_integration_wagle_markpoint.py +
tests/test_markpoint_http_authorization_wave5.py +
tests/test_markpoint_access_wave4.py:
  61 passed, 0 failed, 0 errors, 154.34s  (not previously reported by the
  Developer as part of this task's own "related suites" figure; run here
  for broader independent confidence)

Combined Markpoint-adjacent total: 124 passed, 0 failed, 0 errors
```

### Weekly non-regression

`test_projection_derives_every_figure_from_the_ledger` asserts
`weekly_earned == 30` and `weekly_deducted == 12` in the same run as the
`today_*` assertions above — confirmed PASS in all 5 consecutive runs. No
`rolling_window`/`mission_template` contract file appears in the diff
(independently confirmed absent).

## Cross-environment timezone independence

### OS-local timezone (process `TZ`)

```text
TZ=Asia/Seoul        : 3/3 selected tests passed (2 original + 1 new-deterministic)
TZ=UTC               : 3/3 selected tests passed
TZ=America/New_York  : 1/3 passed -- the 2 ORIGINAL tests FAILED;
                        the 1 new deterministic test still PASSED
```

**Finding QA-F-003** (disclosed, does not block this task's own PASS
component): the two originally-failing tests compute their own `anchor =
date.today()` **inside the test file itself** (naive, OS-local, unrelated to
`service.py`'s fix) and pass it explicitly to `own_projection(anchor=
anchor)`. Under `TZ=America/New_York`, that anchor is the New-York calendar
date, which can differ from the KST calendar date the fix correctly computes
internally for the ledger entry's actual timestamp — causing the test's own
assertion to fail. This is a **pre-existing test-file fragility
(`TEST_ISOLATION_DEFECT`-shaped)**, not introduced by this remediation (the
diff only appends new tests after these two; their bodies are untouched) and
not a defect in the fix itself: `test_projection_kst_boundary_independent_
of_server_local_timezone` — which uses an explicit fixed anchor rather than
`date.today()`, exactly the pattern the two older tests lack — passed
identically under all three `TZ` settings, directly proving the *product
code*'s own OS-timezone independence. The two older tests happen to pass in
both the Developer's environment and this one only because both machines'
default OS timezone is KST-equivalent; a CI runner set to a non-KST timezone
would silently fail them for a reason unrelated to product correctness.

### DB session timezone

```text
ALTER DATABASE mc_qa_markpoint_verify SET timezone TO 'UTC';
  (process TZ=Asia/Seoul, i.e. the exact mismatch the Developer's own root-
  cause trace described as the live bug condition)
  -> 6/6 selected tests (2 original + 4 new) passed
ALTER DATABASE mc_qa_markpoint_verify RESET timezone;
```

PASS — confirms the fix is independent of the DB session's own `TIMEZONE`
GUC, matching the SQL-level proof in Root Cause Verification above.

## Backend Full Suite

```text
collected total: 404 (pytest --collect-only, independently collected, not
  copied from the Developer's own 404 figure)

Run A:
  passed:   404
  failed:   0
  errors:   0
  duration: 709.01s
  warnings: 943 (pre-existing Pydantic/jose deprecation warnings, unrelated)

Run B (immediately following, same DB, no reset/recreation/selection change,
  no code change):
  passed:   404
  failed:   0
  errors:   0
  duration: 1006.44s
  warnings: 943
```

Both runs passed cleanly on the first attempt; the `KNOWN-W7-5-WAGLE-
CONCURRENCY-001` intermittent condition (registered in `COVERAGE_MAP.md`,
pre-existing, unrelated to this task) did not manifest in either run. This
is genuinely-independent evidence of the two-consecutive-clean-runs gate,
not a re-statement of the Developer's own Closure Verification pass (which
used a different disposable DB on Docker port 15435).

## Hardening Smoke

```text
Migration 0021 + Board-room concurrency + Admin bcrypt
  (tests/test_migration_0021_participant_merge.py +
   tests/test_wagle_integration.py + tests/test_auth_admin_login.py):
  34 passed, 0 failed, 0 errors, 91.04s

E2E runner (tests/e2e/scripts/run-w75-full-spec.sh): NOT RUN.
  Classification: ENVIRONMENT_REQUIRED (Docker unavailable in this WSL QA
  session). Diff-audited above: this remediation touched zero files under
  tests/e2e/, so the runner's own behavior is unchanged by this task
  regardless.
```

## Baseline Integrity

```text
product code QA modification:  0 (service.py byte-identical to HEAD, start and end)
test code QA modification:     0 (test file byte-identical to HEAD, start and end)
migration QA modification:     0
existing dirty damage:         0 (5 pre-existing dirty entries, byte-identical start/end)
runtime artifact:               1 disposable DB (mc_qa_markpoint_verify) created and
                                 dropped; 1 throwaway diagnostic script created and
                                 deleted; scratch logs kept outside the worktree in
                                 this session's own scratchpad, not the repository
credential residue:             0 (QA-only local Postgres role/password, not an
                                 operating credential, never written to a repo file)
temporary infra removed:        confirmed (`select datname ... ` empty post-drop)
persistent dev stack unchanged: confirmed (this session's own separate local
                                 dev.sh-managed mc_festival stack on :8000/:5174
                                 responded 200 after this QA pass, untouched)
production untouched:           not applicable/not reached (no NAS/production
                                 credential or host touched this session)
```

## Findings

### QA-F-001 — EVIDENCE_GAP (governance/documentation staleness, non-blocking)

- **File**: `agent-system/qa/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`, `agent-system/handoffs/active/MONGLE-W7-5-MARKPOINT-PROJECTION-STABILITY-REMEDIATION-001.md`
- **Summary**: Both documents state, multiple times and explicitly, `Commit/push/merge/rebase were not performed`. The fix is in fact already committed (`328d877`) and already present on `origin/dev-newmarkp`.
- **Evidence**: `git log -1 328d877`, `git branch -r --contains 328d877` both confirm.
- **Impact**: No product impact. Governance-record staleness only — a future reader trusting these documents literally would wrongly believe the fix is still an uncommitted working-tree diff.
- **Recommended remediation**: A documentation-only correction (LOCAL-FIX tier) noting the commit, likely by whoever committed/pushed (commit author is `iamsonmac@gmail.com`, plausibly the PM).

### QA-F-002 — Test coverage gap, deducted-side KST boundary (non-blocking, independently closed by QA diagnostic)

- **File**: `backend/tests/test_markpoint_core_gap_wave5.py` (the 5 new tests)
- **Summary**: None of the 5 new deterministic regression tests exercises `today_deducted` at an explicit KST/UTC boundary instant; this task's own Section 13 requires both `earned` and `deducted` coverage in the deterministic set.
- **Evidence**: Per-test table above; standalone diagnostic (Date Boundary Evidence section) confirms the underlying code path is correct for the deducted side too — `_sum_ledger`'s shared `occurred_date_kst` expression handles both `positive=True`/`positive=False` identically.
- **Impact**: No product impact measured. A future regression on the deducted-only path would not be caught by the deterministic suite specifically (only by the non-deterministic, ~9-hour-window-dependent pre-existing test).
- **Recommended remediation**: Add one deterministic `MANUAL_DEBIT`-boundary test mirroring `test_projection_kst_boundary_independent_of_server_local_timezone`. Not performed by this QA pass (product defect boundary — QA does not write permanent test code).

### QA-F-003 — Pre-existing test OS-timezone fragility (non-blocking, predates this task)

- **File**: `backend/tests/test_markpoint_core_gap_wave5.py::test_projection_derives_every_figure_from_the_ledger`, `::test_projection_isolates_date_boundaries`
- **Summary**: Both tests compute `anchor = date.today()` in the test file itself (OS-local, not KST-explicit), making their own PASS/FAIL depend on the executing machine's OS timezone matching KST — confirmed to fail under `TZ=America/New_York` while the fix's own dedicated deterministic test does not.
- **Evidence**: Cross-environment timezone independence section above.
- **Impact**: No product impact — the underlying `service.py` fix is proven OS-TZ-invariant by the deterministic test. Only these two pre-existing tests' own reliability is environment-coupled, and only outside a KST-equivalent host.
- **Recommended remediation**: Out of this remediation task's scope (the two tests predate it and were not modified by it). A future test-hygiene pass could replace their own `date.today()` with an explicit KST anchor.

## 5-Gate Self-Check

- **Hallucination Guard**: root cause re-derived from a live raw-SQL experiment on a real disposable DB, not from re-reading the Developer's deleted diagnostic script; 404 collected count independently run via `pytest --collect-only`; the deducted-side gap was independently verified by writing and running a throwaway script rather than assumed safe from code symmetry alone.
- **Omission Guard**: the commit/push contradiction (QA-F-001), the deducted-side test-coverage gap (QA-F-002), the pre-existing OS-TZ test fragility (QA-F-003), and the un-run E2E smoke (`ENVIRONMENT_REQUIRED`) are all disclosed here rather than silently omitted because they don't block the core verdict.
- **Miswork Guard**: `git diff --check` clean at both start and end; product/test files confirmed byte-identical to HEAD at both start and end; the disposable QA database and the throwaway diagnostic script were both removed; the persistent local dev stack (`dev.sh`) was left running, untouched, and still responsive.
- **Axis Alignment**: this verdict closes only `RE-QA-F-003`'s own code-defect hardening scope. It does not declare `MONGLE_W7_5_HARDENING_FOCUSED_INDEPENDENT_RE_QA_PASS`, `MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`, `MONGLE-W7-4` live-consumer-integration completion, or W7.6 readiness.
- **Freshness/Evidence Consistency**: every number in this report came from a command run in this session against current HEAD (`328d877`) on a database created fresh in this session, not carried forward from the parent Re-QA's own pre-fix numbers or the Developer's own post-fix numbers.

## Verdict rationale

No `FAIL` criterion (Section 24) is met: the KST boundary is correct at
midnight, no `date.today()`/OS-local dependence remains in the product fix,
DB-session-timezone independence is proven, no regression in either
originally-failing test, no new-test failure, no weekly regression, no
Markpoint-suite failure, both full Backend suite runs passed cleanly, no
task-owned failure, the Hardening smoke that *could* run passed, and this QA
pass made zero product/test/migration modification.

Two of the explicit `CONDITIONAL` criteria (Section 24) are met, however:
"비차단 문서 또는 증거 공백" (QA-F-001, QA-F-002, QA-F-003 above) and
"Hardening smoke 일부 환경성 미실행" (the E2E runner, blocked by this QA
session's own lack of Docker). Per this task's own instruction not to treat
an un-run item as a passed one, the verdict is **CONDITIONAL**, not `PASS`.

```text
MONGLE_W7_5_MARKPOINT_PROJECTION_FOCUSED_INDEPENDENT_QA_CONDITIONAL
RE_QA_F_003_INDEPENDENTLY_VERIFIED_CLOSED_FOR_CODE_CORRECTNESS
MARKPOINT_KST_DATE_BOUNDARY_DEFECT_INDEPENDENTLY_VERIFIED_FIXED
MARKPOINT_TODAY_EARNED_INDEPENDENTLY_VERIFIED
MARKPOINT_TODAY_DEDUCTED_INDEPENDENTLY_VERIFIED_VIA_QA_DIAGNOSTIC_NOT_COMMITTED_TEST
MARKPOINT_TIMEZONE_REGRESSION_COVERAGE_PARTIAL_EARNED_SIDE_ONLY_IN_COMMITTED_TESTS
MARKPOINT_PROJECTION_REPEAT_RUN_STABILITY_INDEPENDENTLY_VERIFIED
BACKEND_FULL_SUITE_TWO_CONSECUTIVE_RUNS_INDEPENDENTLY_VERIFIED
TASK_OWNED_FAILURE_ZERO
E2E_RUNNER_SMOKE_ENVIRONMENT_REQUIRED_NOT_RUN
W7_5_CODE_DEFECT_HARDENING_SCOPE_CONDITIONALLY_CLOSED_PENDING_QA_F_001_QA_F_002_DISPOSITION
OVERALL_W7_5_REMAINS_CONDITIONAL_HUMAN_GATE
```

Not declared, per this task's own Section 26 restriction:
`MONGLE_W7_5_DATA_AND_BEHAVIOR_WIRING_PASS`,
`FULL_PRODUCT_BEHAVIOR_WIRING_COMPLETE`, `PM_DECISIONS_RESOLVED`,
`W7_4_LIVE_CONSUMER_INTEGRATION_PASS`,
`READY_FOR_W7_6_COMMON_COMPONENT_EXTRACTION`.

Official status after this pass:

```text
W7.5 code-defect hardening (RE-QA-F-003 lineage): CONDITIONAL
  (pending PM disposition of QA-F-001/QA-F-002/QA-F-003 and an E2E smoke
  run in a Docker-capable environment)
W7.5 overall: CONDITIONAL / HUMAN_GATE (unchanged)
W7.4: REOPENED, LIVE_CONSUMER_INTEGRATION_AUDIT PENDING (unchanged)
W7.6: BLOCKED (unchanged)
```

Next task (unchanged from the parent chain):
`MONGLE-W7-4-LIVE-CONSUMER-INTEGRATION-AUDIT-001`.

No commit, push, merge, or rebase was performed by this QA pass.
