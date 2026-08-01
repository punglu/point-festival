# MONGLE Target Decision Package Reconciliation

**Task:** `MONGLE-TARGET-DECISION-PACKAGE-RECONCILIATION-001`  
**Target Decision SSOT:** `MONGLE_TARGET_DECISION_FREEZE.md`

## Reconciled package

| Topic | Current evidence document | Target Decision SSOT | Replacement statement |
|---|---|---|---|
| Service entitlement | Family models / Axis B | D5-A | Group service right is distinct from human participation. |
| Human Markpoint actor | Markpoint contract | D5-B | **Approved:** FamilyMembership identity; no separate MarkpointParticipant at this stage; active membership default access after FamilyAdmin-approved/direct activation. |
| Machine events | Doran principal/binding | D5-C | **Approved:** non-human Markpoint `ServicePrincipal` publishes deduplicated, traceable events only to the originating FamilyGroup's approved Wagle room. |
| Wagle realtime | Realtime messaging contract | D6 | **Approved:** WebSocket foreground, Web Push background, durable DB+Outbox SSOT, at-least-once delivery, Room order, idempotency and recovery. |
| Markpoint reuse | Markpoint contract | D5-B/D7 | classify pure logic, contract-review candidates, patterns, and reference-only UX separately. |
| Legacy cutover | cutover gap reports | D8 | **Approved RESET:** no operational-data migration/backfill; empty Target verification, read-only Legacy retention, write freeze and PM retirement gate. |
| Service ownership / registration | family models / Axis B | D5-A1/A2/A3 | Owner Scope, Registrant, User, ServiceAdmin and machine ServicePrincipal are separate; physical model remains unselected. |

## Backlog reconciliation

The approved framework does not authorize all implementation work: service-specific access, activation, retention and physical-model tasks remain `PM_DECISION_REQUIRED`. Wave 1 separates credential, managed account/recovery, sessions, context switch, scoped RBAC, personal/family service ownership and auth UI. Wave 2 separates history/command/outbox/gateway/auth/reconnect/read/delivery/presence/notification/UI. Wave 3 separates human participant lifecycle, ownership adapter, registration/access/lifecycle and UI. Wave 4 separates mission, approval, ledger/balance, level/reward, events and user/manager UI. Wave 5 keeps UI as independent slices, not one task.

D8 Reset/Cutover requires empty Target verification, seed/fixture operational-data isolation, new Account/Family creation, new-ledger invariants, Legacy write freeze/access control, read-only backup, post-cutover verification, audit and PM-approved retirement. No Legacy mapping, backfill, financial reconciliation or Target fallback is part of launch.

## Gate result

- Gate 1: PASS — human/machine identity and current evidence/Target decisions are separated.
- Gate 2: PASS — D5-A/B/C, D6, vertical slices, retention/rollback and test taxonomy are linked.
- Gate 3: PASS — no product/test/DB/migration/shared-agent-system file changed.
- Gate 4: PASS — Mongle platform, Wagle realtime, Markpoint service and Legacy reference boundaries preserved.
- Gate 5: PASS — Decision Freeze is SSOT; Axis B evidence remains usable with supersession boundaries.

`READY_FOR_PM_TARGET_DECISION_REVIEW`

## Addendum — new-screen evidence folded in

The 9 new pre-login/pre-group screens (0a–0g) and the Mongle logo kit added
under `docs/temp/logo and additional pages/` were reviewed against this
package in `MONGLE_NEW_SCREENS_CONTRACT_IMPACT_REVIEW.md`. That review is
evidence-only and changes no row or Gate verdict above; it updates
`MONGLE_TARGET_DECISION_FREEZE.md` (D1/D2/D3/D4/D7 evidence),
`MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md` (Membership lifecycle candidates),
`MONGLE_EPIC_FEATURE_DECOMPOSITION.md`, `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`,
`MONGLE_IMPLEMENTATION_BACKLOG.md` (8 new backlog rows), and
`MONGLE_DOD_AND_TEST_MATRIX.md` (new target-journey examples) with
cross-referenced addenda only. Package status remains
`READY_FOR_PM_TARGET_DECISION_REVIEW`.
