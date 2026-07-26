# Handoff — CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001

- Task ID: `CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001`
- Closeout Contract: `v1`
- Author/agent: `Codex /root/regression_fixture_persistence_writer`
- Branch: `dev`
- Start HEAD: `476e1bc273ffc18bda3e3ca08118170a9c6e3c8e`
- End HEAD: `PENDING_IMPLEMENTATION_COMMIT`
- Final Commit: `PENDING_IMPLEMENTATION_COMMIT`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- secrets_redacted: `true`

## Changed Files

- `agent-system/tests/test_check_closeout.py`
- `agent-system/qa/COVERAGE_MAP.md`
- `agent-system/active.md`
- `agent-system/relay/current.md`
- `agent-system/handoffs/active/CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001.md`
- `agent-system/qa/CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001.md`

## Existing Dirty State

- Unstaged diff SHA-256 at start: `70f7528ca61fa2b79831e02592a884b39c65d2b290346553ecaa22f7218e9b81`
- Staged diff SHA-256 at start: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Untracked paths at start: none.
- Existing user-owned dirty paths were not modified, restored, or staged.

## Historical 23-fixture Investigation

Git handoffs and implementation evidence identify the historical temporary
fixtures by outcome classes, including the original 15 contract cases and the
FIX-001 empty-reason extensions. Their executable `/tmp` definitions were not
committed. The source therefore does not establish every original input
artifact combination. This task preserves that historical evidence as an
execution record and defines a separately counted, source-backed permanent
matrix; it does not guess or claim to reconstruct all 23 historical fixtures.

## Finding 1 Known Gap

`documents_by_task()` first buckets documents by their internal Task ID, which
may make a later mismatch-specific branch unreachable for selected malformed
artifact combinations. This task does not change checker behavior. Record it
as a follow-up candidate for a dedicated checker review.

## Commands and Exit Codes

- `python3 agent-system/tests/test_check_closeout.py`: exit `0`; 13 test
  methods passed. This comprises 10 parser checks, 15 existing archive
  lifecycle subTest cases, and 21 new permanent matrix cases (20 temporary
  task graphs plus one current-repository clean-state case).
- `python3 agent-system/tools/check_closeout.py`: exit `0`; warnings `0`.
- `python3 -m py_compile agent-system/tools/*.py`: exit `0`.
- `python3 agent-system/tools/check_active.py`: exit `0`.
- `python3 agent-system/tools/check_handoff_refs.py`: exit `0`.
- `python3 agent-system/tools/check_decision_ids.py`: exit `0`.
- `python3 agent-system/tools/check_all.py`: exit `0`.
- `git diff --check`: exit `0`.
- `git diff --cached --check`: exit `0`.

## Permanent Regression Matrix

The new matrix invokes the real checker as a subprocess. It covers normal and
invalid OPEN graphs; normal and invalid ARCHIVED graphs; empty no-change
reason and malformed closeout blocks; QA-evidence-only graphs; markerless
historical records; duplicate archived artifacts across months; report-only
exit-zero/no-traceback behavior; and the current repository's warning-free
state. The 15 existing archive lifecycle subTest cases remain separate, and
the 10 existing parser tests remain unchanged.

## QA Status

- Self-check only: `true`
- Verification: `QA_PENDING`
- Independent QA: `pending`

## Drive Evidence

- Git repository is SSOT.
- Drive publication is `ENVIRONMENT_REQUIRED` when no Drive connector is
  available; existing historical artifacts are not modified.

## Next First Action

Run independent QA against the source-backed permanent matrix, parser tests,
archive lifecycle fixtures, static checks, Coverage Map evidence, Finding 1
recording, and existing dirty-state preservation.

## Forbidden Scope

No checker behavior change, CLOSEOUT-001 resumption, archival or graduation,
historical artifact overwrite, dependency/CI/product change, active closure,
or push.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md` contains this open QA-pending task.
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/CLOSEOUT-REGRESSION-FIXTURE-PERSISTENCE-001.md`
- Independent QA: `pending`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: A reproducible source-backed Closeout Contract v1 regression matrix is added without altering checker behavior.
- CLOSEOUT GATE: `PASS`

Closeout Gate PASS records synchronized documentation only. It is not an
independent QA verdict, lifecycle completion, graduation, or push approval.
