# MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001

- Kind: independent QA / test, no product code changes
- Execution Target: `MONGLE-W4-MARKPOINT-MISSION-LEDGER-001`,
  `MONGLE-W5-MARKPOINT-FUNCTIONAL-COVERAGE-GAP-COMPLETION-001`,
  `MONGLE-W5-MARKPOINT-CORE-GAP-CLOSEOUT-001`
- author/agent: `Claude Code`
- created_at: 2026-08-01
- environment: `/Users/mac/mac_Project/mongle_ui`, branch `dev-newmarkp`
- evidence: `agent-system/qa/MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001.md`
- secrets_redacted: true
- Lifecycle: `IN_PROGRESS` (evidence complete; PM decision pending on the
  CONDITIONAL verdict)
- Decision: `DESIGN_APPROVED` (process task; PM's rolling-window/bulk-
  approval/PM-decision-deferral contracts not reopened)
- Verification: `CONDITIONAL` (`PRODUCT_CORE_VERIFIED` /
  `DOCUMENTATION_CORRECTION_REQUIRED`)
- Execution: `SUCCEEDED`
- Closeout Contract: v1
- Branch: `dev-newmarkp`
- Start HEAD / End HEAD: `25c8d0ccfa0406e2b458da7e8ca251ac8737b840`
  (unchanged — no commit performed)

## Backlog tasks addressed

Independent QA of Wave 5 Markpoint Core: Mission lifecycle, per-Family cycle
configuration with both guards, rolling materialization, weekly/daily
projection, append-only deduction correction, level boundaries, admin
filters and bulk approval, HTTP authorization matrix, concurrency, and the
Markpoint-side Wagle relay boundary.

## Worktree and changed files

- Modified: `agent-system/active.md` (this QA's own writer registration
  only, additive).
- New: this handoff, its QA evidence.
- Not touched: any product/migration/frontend file; the concurrent
  `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002` writer's files.

## Commands and outcomes

- Migration: fresh `0000`→`0011`, `downgrade -2`, re-upgrade — single head,
  zero residue, zero legacy backfill, all independently reproduced.
- Five constraint violations actually attempted against the live DB (append-
  only trigger ×2, unique reversal, cycle CHECK, same-family actor FK) — all
  five correctly rejected with the exact expected PostgreSQL error.
- `python -m pytest -q` (disposable DB, fresh container): **312 passed, 0
  failed** — exact match with the reported figure.
- Four concurrency tests confirmed genuinely concurrent (separate
  `AsyncSessionLocal` sessions under `asyncio.gather`) by reading their
  implementation, then re-run and passed.
- Rolling-window arithmetic independently hand-derived against PM's three
  approved examples (Monday/Saturday/Sunday) — exact match.
- `npx tsc --noEmit`: EXIT=0. OpenAPI: 140 paths, doran 0, naran 0
  (re-counted).
- `git diff --check`: clean, start and end.

## Completed / remaining

- Independently verified, no Core defect: migration, all 10
  `COVERED_TARGET` Coverage Matrix rows, cycle guards, rolling
  materialization, projection, deduction correction, level, admin/bulk
  atomicity, HTTP authorization, concurrency, Wagle relay transaction
  boundary and import isolation.
- **One documentation gap found, not fixed (out of this QA's scope):** two
  docstrings (`markpoint_target/service.py::rolling_window` and the legacy
  `mission_template/service.py::get_rolling_window`) still describe the
  rolling window as an unresolved contradiction rather than reflecting PM's
  2026-08-01 approval of the code's actual behavior as the binding
  `TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE` contract. Exact locations and
  required correction text are in QA Evidence §24.
- QA Status: `WAVE_5_INDEPENDENT_QA_CONDITIONAL`.
- Coverage Map: not modified — no row required a change.

## Risks and Human Gate

- PM decision needed on whether to graduate Wave 5 Core now (docstring fix
  as a trivial tracked follow-up) or require the two-line fix first — this
  QA cannot itself edit product source under its own scope restriction.
- No commit or push was made.

## Next agent first action

PM review of the CONDITIONAL verdict. If accepted, either graduate Wave 5
Core with the docstring correction tracked separately, or have the next
writer make the two documented docstring edits (§24 of QA Evidence gives
exact file/line/required-text) and re-confirm before graduation — no other
re-verification is needed, since this QA found zero Core product defects.

## Forbidden Scope (as declared, respected throughout)

Product service/router/model changes, migrations, frontend product code,
permission policy, weakening any existing product test assertion, any file
owned by the concurrent `PHASE0-AGENT-SYSTEM-RECORD-INTEGRITY-AUDIT-002`
writer.

## Closeout Synchronization

- Contract: v1
- HANDOFF: `UPDATED` — this file
- QA EVIDENCE: `UPDATED` — `agent-system/qa/MONGLE-W5-MARKPOINT-INDEPENDENT-QA-001.md`
- Independent QA: `this is the independent QA` — `CONDITIONAL`
- COVERAGE MAP: `NOT_MODIFIED_BY_THIS_SESSION`
- CLOSEOUT GATE: `PASS` (documentation obligations synchronized; product
  Verification stays `CONDITIONAL` pending the docstring correction, which
  is a separate axis from this closeout gate)
