# MONGLE Service Ownership / Registration Reconciliation

**Task:** `MONGLE-SERVICE-OWNERSHIP-REGISTRATION-CONTRACT-RECONCILIATION-001`  
**Decision SSOT:** `MONGLE_TARGET_DECISION_FREEZE.md`  
**Scope:** documentation contract reconciliation only; no product, test, DB, migration, API, or shared agent-system files changed.

## Measured workspace

- Worktree: `/Users/mac/mac_Project/mongle_ui`
- Branch / exact HEAD: `dev-newmarkp` / `da7ea7403aefef33a90d622940724b0c53ee8873`
- Start status: dirty from pre-existing parallel work, including shared agent-system, Avatar, test-governance, and prior phase2 documentation changes.
- Active parallel worktree observed: detached data-backend contract worktree at `/private/tmp/claude-501/-Users-mac-mac-Project-mongle-ui/7815dbc1-d883-4eb4-9a83-5a314e2261e5/scratchpad/data-backend-contract-worktree`.
- This task modified only the listed `engineering/phase2/` documentation files and created this report; it did not touch shared-session files.

## Reconciled contract

| Concept | Contract |
|---|---|
| Service Definition | logical policy definition; declares allowed owner scopes, registration, activation, access, admin, retention and Push policy |
| Service Instance | logical actual-use unit for an Account or FamilyGroup; not a newly asserted table/model |
| Registrant | actor requesting, registering or activating a service |
| Owner | Account for personal instance; FamilyGroup for family instance |
| User | Account or FamilyMembership granted service access |
| ServiceAdmin | explicit service-scoped operating role |
| ServicePrincipal | non-human system actor for service events |

`REGISTRANT ≠ OWNER ≠ USER ≠ ADMIN ≠ SERVICE_PRINCIPAL`. Equality is possible in a concrete policy but is never implied by registration.

## Approved decisions preserved and extended

- D1–D4 remain unchanged.
- D5-A remains approved and now explicitly applies to Core Capability and **Family-owned** service entitlement only.
- D5-A1 approves owner scopes: `CORE_FAMILY`, `PERSONAL`, `FAMILY`, `PERSONAL_OR_FAMILY`.
- D5-A2 approves registrant/owner/user/admin/principal separation and policy-permitted FamilyMember registration/request.
- D5-A3 approves the four family activation-policy modes.
- D5-B is approved for Markpoint: FamilyMembership is human identity, active Membership gets default access after FamilyAdmin-approved/direct activation, and no `MarkpointParticipant` is introduced at this stage.
- D5-C is approved: Markpoint uses the non-human `ServicePrincipal` system actor for FamilyGroup-scoped Wagle events; physical reuse fit remains an implementation validation, not a different product decision.

## Service mapping

| Service | Confirmed mapping | Explicitly unresolved |
|---|---|---|
| 와글와글 | `CORE_FAMILY`; FamilyGroup owner; FamilyMembership human identity; auto enable; no Subscription gate | detailed Room/retention policy under D6 |
| Markpoint | `FAMILY`; **FamilyGroup owner (approved)**; **FamilyMembership human identity (approved)**; member request → FamilyAdmin approval or FamilyAdmin direct activation; `ACTIVE` Membership default access, which is not forced participation; explicit ServiceAdmin only, registrant never auto-admin; **no `MarkpointParticipant` aggregate** | nothing on this row remains unresolved — D5-B closed all of it. Physical schema/API realisation is implementation work |
| 가계부 | `PERSONAL_OR_FAMILY`; Account personal instance vs FamilyGroup family instance are isolated | activation, access, visibility, admin and retention policy |

## Backlog and test linkage

Six candidate backlog tasks are recorded in `MONGLE_IMPLEMENTATION_BACKLOG.md`; each remains `PM_DECISION_REQUIRED` until a concrete service policy is approved. The DoD/Test Matrix adds personal privacy, registration approval/denial, registrar lifecycle, owner-scope isolation and Push revalidation journeys.

## Validation

- `git diff --check`: PASS
- Product code changed: no
- Test code changed: no
- DB/migration changed: no
- Shared `agent-system/` changed: no
- `python3 agent-system/tools/check_all.py`: exit 0. Existing unrelated warnings: two handoff paths outside the active-handoff directory, and missing QA evidence/Closeout Synchronization for `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2`. No new error reported for this task.

## Five gates

- Gate 1 — 환각: PASS — logical terms are not claimed as tables; Markpoint and ledger detail decisions remain pending.
- Gate 2 — 누락: PASS — personal/family/mixed scope, actors, lifecycle, Push, backlog and test journeys are linked.
- Gate 3 — 오작업: PASS — no code, DB, migration, test, or shared agent-system edits.
- Gate 4 — 중심축: PASS — D1 family communication boundary, D4 role separation and Wagle core capability remain intact.
- Gate 5 — Stale·근거: PASS — D5-A scope and D5-B wording are corrected in the Decision SSOT and linked documents.

## Result

`READY_FOR_PM_SERVICE_SPECIFIC_ACCESS_DECISIONS`

**Remaining PM decisions:** household-ledger and future-service-specific activation/access/retention policies only.  
**Next authorized action:** `PM_REVIEW_MARKPOINT_ACCESS_POLICY`
