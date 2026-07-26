# PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001

- Task ID: `PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001`
- Closeout Contract: `v1`
- Branch: `dev`
- Start HEAD: `93b769079027a06ccd7a42cd78c361cd25d50f52`
- End HEAD: `pending — implementation documentation commit`
- Final Commit: `pending — implementation documentation commit`
- Existing Dirty State: `CLAUDE.md` modified; four root prompt files and ten `docs/` files deleted. These user-owned changes are out of scope.
- Scope: local canonical engineering-guide localization from the specified Drive sources and drafts, based on a read-only repository audit.
- Forbidden Scope: product code, dependencies, Docker/Compose, DB schema/migrations, tests, runtime changes, Drive writes, and push.

## Source audit

Directly read Drive originals: Outlook Hub Backend and Frontend guides; Viblot Common, Backend, and Frontend DRAFTs. Directly read Drive family-platform drafts: README, Common Norms, Backend, Frontend, Testing, and Provenance/PM Gates.

Repository audit samples include `backend/app/main.py`, `database.py`, `config.py`; auth, mission, daily-point, chat, admin, and mission-template domains; `database/init.sql`; `frontend/src/App.tsx`, Auth, UserDashboard, AdminDashboard, shared HTTP/auth state; package, Compose, pytest, and Playwright configuration.

## Planned deliverables

- `engineering/README.md`
- `engineering/COMMON_NORMS.md`
- `engineering/BACKEND_GUIDE.md`
- `engineering/FRONTEND_GUIDE.md`
- `engineering/TESTING_GUIDE.md`
- `engineering/PROVENANCE_AND_PM_GATES.md`

## Implementation result

- Added an `engineering/` canonical-guide index and five localized guides.
- Added only a thin `AGENTS.md` link; detailed policy remains in `engineering/`.
- Classified verified repository facts as CURRENT, imported desired practices as
  TARGET, retained variations as LEGACY, and bounded unresolved architecture to
  five PM gates.
- Changed Files: `AGENTS.md`; `engineering/README.md`;
  `engineering/COMMON_NORMS.md`; `engineering/BACKEND_GUIDE.md`;
  `engineering/FRONTEND_GUIDE.md`; `engineering/TESTING_GUIDE.md`;
  `engineering/PROVENANCE_AND_PM_GATES.md`; task active/relay/handoff/evidence.

## Commands and exit codes

- Direct Drive reads: five originals and six family-platform drafts, completed.
- Repository path/contract audit: completed read-only.
- `python3 agent-system/tools/check_closeout.py`: exit 0, warning 0.
- `python3 agent-system/tools/check_all.py`: exit 0, warning 0.
- `git diff --check`: exit 0.
- `git diff --cached --check`: exit 0 before staging.

## Known gaps and next action

- No source-only audit can establish production, device, or operating-DB PASS.
- PM review must select, defer, or reject PM_GATE-01 through PM_GATE-05; no gate
  is implemented by this documentation task.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE0-DEVELOPMENT-GUIDE-LOCALIZATION-001.md`
- Independent QA: `not_applicable — documentation localization; PM review required`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: guide localization adds no executable test, behavior, tier, journey, or execution evidence.
- CLOSEOUT GATE: `PASS`
