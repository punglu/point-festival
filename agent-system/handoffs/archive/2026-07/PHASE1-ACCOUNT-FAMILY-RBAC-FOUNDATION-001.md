# PHASE1-ACCOUNT-FAMILY-RBAC-FOUNDATION-001

- Task ID: `PHASE1-ACCOUNT-FAMILY-RBAC-FOUNDATION-001`
- author/agent: `Codex`
- created_at: `2026-07-26`
- git_ref: `fa6fb65d1a79a01342da9695a9156f08a0e5f1fb`
- environment: `local macOS workspace; isolated synthetic database only`
- secrets_redacted: `true`
- Lifecycle: `COMPLETED`
- Decision: `DESIGN_APPROVED`
- Verification: `PASS`
- Execution: `SUCCEEDED`
- Closeout Contract: `v1`
- Branch: `dev`
- Start HEAD: `fa6fb65d1a79a01342da9695a9156f08a0e5f1fb`
- End HEAD: `candidate recorded by the final evidence commit; independent QA will
  measure the immutable candidate HEAD`
- Final Commit: `the final test/evidence commit is self-referential; its exact
  hash is recorded by independent QA and the final implementation report`

## Scope

Implement approved Account/Family/Membership/multirole Permission Foundation,
legacy identity adapter, path-scoped family APIs, frontend context, Alembic
baseline/foundation migration, and synthetic API+DB regression evidence.

## Forbidden scope

No operating DB/NAS access, legacy login/JWT cutover, Player or legacy role
removal, legacy business-table family-FK retrofit, calculation change, Doran room
model, multi-device sessions, explicit grants/denies, user-owned dirty change,
or push before independent QA PASS.

## PM decisions applied

Multiple active owners (minimum one), unified scoped roles, path-based Family
context, no explicit grant/deny in v1, and reviewed legacy bootstrap mapping.
Relationship is never an authorization predicate.

## Existing dirty state

User-owned `CLAUDE.md` modification and root/docs deletions; start unstaged
SHA-256 `eae6f749b838eedb02780242c71d6cc285f97335f39d0728669f593877cbdf5f`.

## Changed files and implementation

- Changed Files: approved Phase 1 documents; Alembic async environment and
  `0000` baseline/`0001` Foundation revision; Family domain models, service,
  router, schemas, seed script; isolated `mc_phase1` Compose; frontend family
  context API/store/loader; API+DB suite; task evidence and Coverage Map.
- Account adapter: current legacy player/admin JWT identities resolve only via
  explicit linked `legacy_identity_mappings`; unmapped/ambiguous identities do
  not receive Family access. Legacy login/JWT and `/dashboard` remain intact.
- Authorization: path-scoped Family APIs evaluate active Account, Membership,
  Role-Permission union, subscription status for SERVICE roles, then resource
  Family boundary. Relationship is never a guard.
- Owner: multiple active owners are allowed; last-owner role removal or
  membership deactivation returns conflict and locks the Family row during the
  count/update decision.
- Bootstrap analysis: `backend/scripts/phase1_legacy_bootstrap_report.py` is
  read-only and emits only aggregate, non-identifying inventory counts. It never
  creates mappings or infers Accounts, Owners, or Relationships.

## Commands and outcomes

- `python3 -m py_compile ...`: exit 0.
- `docker compose -p mc_phase1 ... config --quiet`: exit 0; isolated ports are
  PostgreSQL `15434`, API `18001`, frontend `13001` because 15433 was already
  occupied by an unrelated project.
- Isolated Alembic `upgrade`, `downgrade 0000`, `stamp 0000`, and re-`upgrade`:
  exit 0. No operating DB stamp occurred.
- `backend/scripts/phase1_seed_synthetic.py` plus
  `tests/api/phase1_rbac_api_test.py`: exit 0; 24 reported API/DB assertions.
- Frontend lint/build: exit 0. Backend pytest: 6 passed.
- Existing Phase 0: weekly 6/6, legacy authorization suite PASS, scenario
  87/87, and Playwright 9 passed.

## Known gaps and Human Gates

- Operating schema comparison/stamp, reviewed bootstrap Owner mapping, actual
  identity migration, physical devices/Push, and multi-device sessions are not
  performed.
- Explicit grant/deny, Doran room model, legacy business-table family-FK
  retrofit, and legacy JWT cutover remain excluded.
- Drive publication was not requested; Git is SSOT.

## Independent QA Correction In Progress

Independent QA against candidate `594d858` found four blockers before push:

1. an Admin could set a Family lifecycle status through the service-management
   permission;
2. a closed/suspended Family could remain in account context with permissions;
3. an already-issued legacy JWT did not re-check soft-deleted legacy identity
   state; and
4. the API+DB suite default DB name/user did not match the committed Phase 1
   Compose contract.

The writer is correcting only these authorization and test-reproducibility
issues, adding regression coverage, and will request QA re-verification. This
record preserves the initial QA block rather than replacing it with a PASS.

## Correction Self-check

- Family status changes now require `family.ownership.manage`; an Admin receives
  `403`, while an Owner can perform the explicit lifecycle action.
- Account context/listing joins only active, non-deleted Families, and effective
  permissions for a non-active Family are the empty set.
- The legacy adapter re-checks the current PlayerAuth/AdminAuth and linked
  Player soft-delete state before accepting a pre-existing JWT.
- The API+DB suite now defaults to the committed isolated Compose credentials.
  With no DB override variables, the suite passed all `30` reported checks.

## Independent QA Final Verdict

- Verdict: `PASS`
- QA scope: migration head/idempotent upgrade, default-deny Foundation routes,
  cross-Family path and membership-ID substitution, multi-role/subscription
  gating, multiple-Owner invariant, inactive Family context/path behavior,
  Player/Admin soft-delete adapter behavior, legacy compatibility, static
  checks, and dirty-state preservation.
- Historical QA result: the initial `BLOCKED / RBAC CORE DEFECT` finding is
  preserved above. The correction was independently reverified without product
  scope expansion.
- Push condition: independent QA condition is satisfied; operating DB stamp,
  reviewed bootstrap mapping, and actual identity migration remain Human Gates.

## Closeout Synchronization

- Contract: `v1`
- ACTIVE: `UPDATED`
- ACTIVE Evidence: `agent-system/active.md`
- HANDOFF: `UPDATED`
- HANDOFF Path: `agent-system/handoffs/archive/2026-07/PHASE1-ACCOUNT-FAMILY-RBAC-FOUNDATION-001.md`
- QA EVIDENCE: `UPDATED`
- QA Evidence Path: `agent-system/qa/PHASE1-ACCOUNT-FAMILY-RBAC-FOUNDATION-001.md`
- Independent QA: `complete — PASS`
- COVERAGE MAP: `UPDATED`
- COVERAGE MAP Reason: `new executable API/DB tests are in scope and will be recorded with measured execution evidence`
- CLOSEOUT GATE: `PASS`
