# MONGLE Test Governance Porting Report

## Task record

| Field | Value |
| --- | --- |
| Task | `MONGLE-TEST-GOVERNANCE-PORTING-001` |
| Worktree | `/Users/mac/mac_Project/mongle_ui` |
| Branch | `dev-newmarkp` |
| Exact HEAD | `6c633679c6708a21920f0e4b306bc1e36a2ea72d` |
| Start Status | Pre-existing dirty Avatar files, a pre-existing Phase 0 QA record, and pre-existing Avatar handoff/QA files; preserved. |
| End Status | Governance documents plus this task records changed; no commit authorized. |

## Read-gate inventory

| Document or system | Expected role | Actual path | Exists | Current-content summary | Overlap | Stale risk | Proposed action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Coverage Map | Coverage status | `agent-system/qa/COVERAGE_MAP.md` | Yes | Historic test/evidence index | Prior map mixed tier/evidence with no status schema | Historic rows were not re-run | Normalize schema, preserve rows, mark port-only confidence `NOT_CONFIRMED`. |
| Test Policy | Operating rules | `agent-system/qa/TEST_POLICY.md` | Yes | Bottom-up tiers/evidence policy | Lacked requested taxonomy/feature safety-net rules | Old tiers could be misread as execution tiers | Expand this SSOT; no duplicate policy. |
| Tests README | Commands/environment/artifacts | `tests/README.md` | No | — | — | Commands could be invented | Create from package/config/script reads. |
| Test Agent | Independent verifier | `.claude/agents/test-agent.md` | No | — | — | Agent could rely on session summaries | Create and link SSOTs. |
| FE Guide | Frontend release contract | `engineering/FRONTEND_GUIDE.md` | Yes | Current/target FE practices | No completion gate | Test selection could drift | Add linked release gate/audit boundary. |
| BE Guide | Backend release contract | `engineering/BACKEND_GUIDE.md` | Yes | Current/target BE practices | No completion gate | API/DB verification could drift | Add linked release gate/audit boundary. |
| CLAUDE.md | Thin navigation | `CLAUDE.md` | Yes | Bootstrap links only | Would duplicate policy if expanded | Stale long policy | Add short linked rule only. |
| Package scripts | Command source | `frontend/package.json`, `tests/e2e/package.json` | Yes | npm frontend checks; E2E test/headed only | No Mongle npm script | Do not invent scripts | Document explicit config command; use `SCRIPT_NOT_YET_DEFINED`. |
| Playwright | Browser projects | `tests/e2e/playwright*.config.ts` | Yes | Phase0 default plus Mongle 5-project isolated config | Default and Mongle runtime differ | Runtime availability is volatile | Link actual configs/cleanup; no execution. |
| Pytest | Python config | `backend/pytest.ini` | Yes | Async pytest settings | No root command script | Environment not re-run | Record actual measured invocation only. |
| Agent System QA | Task evidence | `agent-system/qa/` | Yes | Policy/map/task evidence convention | New governance task required record | Shared state is high risk | Register task/handoff/evidence under Closeout Contract v1. |

## SSOT role table

| Role | SSOT |
| --- | --- |
| Coverage status | `agent-system/qa/COVERAGE_MAP.md` |
| Operating policy | `agent-system/qa/TEST_POLICY.md` |
| Commands/environment/secrets/artifacts/cleanup | `tests/README.md` |
| Independent Test Agent | `.claude/agents/test-agent.md` |
| Regression candidate backlog | `tests/e2e/REGRESSION_CANDIDATES.md` |
| FE/BE release gates | `engineering/FRONTEND_GUIDE.md`, `engineering/BACKEND_GUIDE.md` |

The requested `tests/e2e/TEST_POLICY.md` and `tests/e2e/COVERAGE_MAP.md` were
not created: `AGENTS.md` explicitly assigns those roles to `agent-system/qa/`.
Creating duplicates would violate the one-SSOT rule. The Test Agent therefore
reads the actual canonical paths directly.

## Files

Created: `tests/README.md`, `tests/e2e/REGRESSION_CANDIDATES.md`,
`.claude/agents/test-agent.md`, this report, and this task's handoff/QA
evidence. Modified: `agent-system/qa/TEST_POLICY.md`,
`agent-system/qa/COVERAGE_MAP.md`, `engineering/FRONTEND_GUIDE.md`,
`engineering/BACKEND_GUIDE.md`, `engineering/TESTING_GUIDE.md`, `CLAUDE.md`,
`AGENTS.md`, `agent-system/active.md`, and `agent-system/relay/current.md`. Untouched
parallel-session files: DATA-A deliverables, the A1 worktree, Avatar product
and test files, and all existing Wave 6.1 QA evidence.

## Ported policy and application

- Coverage statuses, formulas, confidence, and risk-based lifecycle targets.
- Feature-completion safety net and existing-test-first sequence.
- Golden Journey skeleton (`GOLDEN_JOURNEY_FRAMEWORK: SKELETON_READY`) with
  only evidence-backed candidate identifiers; no forced inventory.
- Tier A/B/B Conditional/C safety skeleton; no package-script changes.
- Eight BLOCKED categories, six executed-failure categories, data-safety order,
  synthetic fixture requirements, and emergency-patch constraints.
- `REG-NNN` candidate structure, Test Agent autonomy/approval/defect boundary,
  and Test Agent verdicts.
- FE/BE release gates separate from existing-debt audits.
- Backend giant-source prevention: router logic is moved to service rather than
  split into subrouters; only explicit query/command/lifecycle service slices
  are allowed; size alone never triggers work; any decomposition is a separate
  approved task with dotted-call patch seams. The current absence of a lint or
  static enforcement guard is documented rather than hidden.

No policy was copied as a second definition into the guide, Test Agent, or
README. Those documents link to the policy. Existing `engineering/TESTING_GUIDE.md`
was reduced to a link for the same reason.

## Stale risk and unconfirmed items

Existing Coverage Map rows retain their historical execution summaries but are
`NOT_CONFIRMED` for this task because neither tests nor runtime were rerun.
The map does not claim a current percentage; the formulas are available only
after a separately authorized baseline audit. Actual Docker availability,
physical-device coverage, secrets, and safe fixture condition are unmeasured.

## What was not ported

- No full product Coverage Map audit: reserved for
  `MONGLE-TEST-COVERAGE-BASELINE-AUDIT-001`.
- No Golden Journey count or new product journey was invented.
- No script, CI, fixture framework, or test was added.
- The absent root-level `CLAUDE_FE_GUIDE.md` and `CLAUDE_BE_GUIDE.md` were not
  fabricated; their actual canonical equivalents are the engineering guides.

## Development use

At feature completion, developers start at the map, select and run the
existing relevant lifecycle test using the README, add only one clear-value
test if unprotected, then update the map from actual evidence. A separate Test
Agent rereads source/diff/tests and issues its defined verdict without fixing a
product defect. Legacy debt is registered for PM-approved separate repair.

## Follow-up candidates

- `MONGLE-TEST-COVERAGE-BASELINE-AUDIT-001` — only after authorization; derive
  confirmed rows/ratios from source and actual execution.
- `REG-001` review only if repeated timestamp-driven visual-delta behavior
  materially affects future test selection.

## Final gates

| Gate | Result |
| --- | --- |
| Gate 1 — 환각 | PASS |
| Gate 2 — 누락 | PASS |
| Gate 3 — 오작업 | PASS |
| Gate 4 — 중심축 | PASS |
| Gate 5 — Stale·근거 | PASS |

`git diff --check` passed. `python3 agent-system/tools/check_all.py` completed
with only pre-existing unrelated warnings for the Doran R2 records and external
A1/DATA-A handoff locations. No repository Markdown-link checker was found;
new/changed local links were resolved manually. This document does not claim an
E2E, Foundation, Avatar, A1, or DATA-A verification result.

Final Verdict: `PASS: MONGLE_TEST_GOVERNANCE_READY_FOR_MAIN_DEVELOPMENT`

Next Authorized Action: `WAIT_FOR_DATA_A_RESULT`
