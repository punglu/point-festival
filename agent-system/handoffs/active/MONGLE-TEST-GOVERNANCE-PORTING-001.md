# MONGLE-TEST-GOVERNANCE-PORTING-001

- Task ID: `MONGLE-TEST-GOVERNANCE-PORTING-001`
- Closeout Contract: `v1`
- Branch: `dev-newmarkp`
- Start HEAD: `6c633679c6708a21920f0e4b306bc1e36a2ea72d`
- End HEAD: unchanged (no commit authorized)
- Scope: documentation-only governance port and Agent System records.
- Forbidden scope observed: product/test code, scripts/config/CI, Docker/E2E,
  DB/API, Foundation/Avatar QA, A1 integration, and DATA-A deliverables.

## Measured start context

- Worktree: `/Users/mac/mac_Project/mongle_ui`
- Existing dirty files preserved: `agent-system/qa/PHASE0-DOC-STALENESS-PREVENTION-001.md`,
  Avatar source/test files, and Avatar task handoff/QA evidence.
- Parallel worktrees: DATA-A scratchpad and contract worktrees, plus the A1
  visual worktree; none were edited.

## Result

The existing Agent System policy and Coverage Map were schema/operating-rule
aligned rather than duplicated under `tests/e2e/`, because `AGENTS.md` declares
their current canonical location. `tests/README.md` owns execution guidance;
the Test Agent points to all three SSOTs. Existing rows were preserved as
schema-normalized historical evidence and marked `NOT_CONFIRMED` for this
non-execution port. The one Golden Journey candidate pair is a skeleton only.

## Follow-up documentation correction

At PM direction, `AGENTS.md` and `CLAUDE.md` received only thin links to the
Test Policy, test command guide, and applicable FE/BE guides. No policy text is
duplicated there; the engineering guides retain their own release-gate detail.

The PM-provided giant-source prevention policy was then localized in
`engineering/BACKEND_GUIDE.md` as a TARGET CONTRACT: no size-only split,
one domain router, service-only query/command/lifecycle decomposition,
separate-task approval, dotted module-call seams, and a documented absence of
an automated guard. No backend source, test, lint, or configuration changed.

## Commands and outcomes

- Read start-gate Git/worktree state and mandatory Agent System files.
- Read existing policy/map, actual package files, Playwright/Pytest config,
  specs, engineering guides, task-record conventions, and artifact scripts.
- No Docker, E2E, pytest, API, DB, or product-code command ran.
- See task QA evidence for static/document verification results.

## Not independently measured

- Historical test assertions and execution claims in pre-existing map rows were
  not re-run; confidence is `NOT_CONFIRMED` by design.
- No production/operating DB, device, or secret availability claim is made.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/MONGLE-TEST-GOVERNANCE-PORTING-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/MONGLE-TEST-GOVERNANCE-PORTING-001.md`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: policy schema/status/confidence/lifecycle alignment is
  this task's explicit deliverable; no execution result was added.
- CLOSEOUT GATE: `PASS`

## Next action

`WAIT_FOR_DATA_A_RESULT`
