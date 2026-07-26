# PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001

- Task ID: `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001`
- author/agent: `Codex`
- created_at: `2026-07-26`
- git_ref: `cc23457e05f01fb2c0684a35478a712da898b801`
- environment: `local macOS workspace; repository and Google Drive decision evidence`
- secrets_redacted: `true`
- Lifecycle: `IN_PROGRESS`
- Decision: `DESIGN_APPROVED`
- Verification: `NOT_TESTED`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev`
- Start HEAD: `cc23457e05f01fb2c0684a35478a712da898b801`
- End HEAD: `document-only closeout commit includes this handoff; final hash is reported outside this self-referential record`
- Final Commit: `self-reference intentionally omitted; see final task report`

## Scope

Define the Phase 1 Account, Family Group, Membership, multirole RBAC, permission,
legacy identity mapping, migration, and Foundation implementation contracts. This is
a document-only target design grounded in the approved Drive decision and measured
legacy source. It must not alter product runtime behavior.

## Intended files

- `engineering/phase1/ACCOUNT_FAMILY_RBAC_CONTRACT.md`
- `engineering/phase1/ACCOUNT_FAMILY_RBAC_DATA_MODEL.md`
- `engineering/phase1/PERMISSION_MATRIX.md`
- `engineering/phase1/LEGACY_IDENTITY_MAPPING_PLAN.md`
- `engineering/phase1/AUTHORIZATION_THREAT_MODEL.md`
- `engineering/phase1/PHASE1_FOUNDATION_IMPLEMENTATION_PLAN.md`
- task records in `agent-system/`

## Existing dirty state

User-owned `CLAUDE.md` modification and root/docs deletions; start unstaged SHA-256:
`eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`.
They are forbidden from staging, modification, restoration, or commit.

## Evidence and constraints

- PM source: Drive document `PM-DECISION-RBAC-MULTIROLE-001`, directly read on
  2026-07-26 (ID `12J43Bd7BEdxPxLupJv9vsQlKf133kWicaka8tkLKVO4`).
- Git is SSOT; Drive is a decision/evidence layer.
- No schema, migration, backend/frontend code, dependency, runtime, or push work.
- The existing MarkPoint system remains `LEGACY REFERENCE / NOT FULLY VALIDATED`.

## Measured current model

- Backend: global JWT `role` (`player`/`admin`) in `backend/app/dependencies.py`;
  Player PIN credentials in `player_auth`; separate administrator username/password
  credentials in `admin_auth`; current routes resolve self ownership through Player IDs.
- Database: all measured domain rows reference `players.id`; no Account, Family
  Group, Membership, permission, or family-scoped resource FK exists.
- Frontend: Zustand restores a global role from the JWT and uses `/dashboard` and
  `/admin/*` UX guards; it has no current-family or permission state.

## Design output

Six target documents define the Account/Family/Membership contract, candidate
data model/invariants, permission matrix, mapping/rollback approach, threat
controls, and sequenced Foundation packages. Five PM Gates remain: owner policy,
role scope storage, family-context wire contract, v1 grants/denies, and initial
Family mapping. No PM Gate is silently implemented.

## Commands and results

- `git diff --check`: exit 0.
- `git diff --cached --check`: exit 0.
- `python3 agent-system/tools/check_closeout.py`: exit 0, warning 0.
- `python3 agent-system/tools/check_all.py`: exit 0, warning 0.
- Markdown local-link, term, permission/matrix, and document-path checks: passed.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/active/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001.md`
- Independent QA: `not_applicable — contract design; implementation QA required`
- COVERAGE MAP: `NO_CHANGE_REQUIRED`
- COVERAGE MAP Reason: `this task defines target contracts only; it adds no executable product test, test behavior, or execution evidence`
- CLOSEOUT GATE: `PASS`
