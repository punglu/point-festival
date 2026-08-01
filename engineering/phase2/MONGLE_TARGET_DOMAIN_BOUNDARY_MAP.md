# MONGLE_TARGET_DOMAIN_BOUNDARY_MAP

> Target boundary decisions are governed by `MONGLE_TARGET_DECISION_FREEZE.md`, including D5-A/A1/A2/A3/B/C and D6. `ServiceInstance` and `ServiceAccessBinding` in that contract are logical terms, not implemented-table claims.

**D1 approved boundary:** FamilyGroup is the organisation and communication boundary. A Room and human Participant never cross FamilyGroups; Room/message/read/notification state is isolated per FamilyGroup even for an Account with multiple FamilyMemberships. `ActiveFamilyContext` selects foreground work and does not suppress authorized background delivery.

**D5 approved ownership boundary:** a service definition may support `CORE_FAMILY`, `PERSONAL`, `FAMILY`, or `PERSONAL_OR_FAMILY`. Account owns and identifies personal services; FamilyGroup owns and FamilyMembership identifies family services. Registrant, Owner, User, ServiceAdmin and machine ServicePrincipal are distinct relationships. Family-owned entitlement does not mean every optional service is Family-owned.

**D7 approved route/API boundary:** Family-owned routes use `/families/{familyId}/...`; Account-owned personal routes use `/me/...`. ActiveFamilyContext is navigation convenience only. The server revalidates Session, Membership/status, Owner Scope or entitlement, Role/Permission and target resource ownership; route shape is not an endpoint-implementation claim.

**Multi-family delivery boundary:** ActiveFamilyContext scopes foreground work only. Account/Device realtime delivery is multiplexed across the server-derived AuthorizedFamilySet; cross-family access remains denied while background notifications, independent unread/cursor state and failure isolation remain per FamilyGroup.

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B), frozen against
`MONGLE_TARGET_DECISION_FREEZE.md` D1–D8 (`APPROVED`, 2026-08-01).

**D1 approved naming:** 몽글 is a **family platform**, not a generic Group
platform. The organisational boundary is `FamilyGroup` and the physical names
`family_groups` / `family_memberships` are approved and retained. A generic
`groups` / `group_memberships` / `group_type` model is **not** part of the
Target contract and must not be introduced. Where older prose in this document
says "Group", read `FamilyGroup`.

Three-layer product structure:

```text
몽글 (Mongle) — family platform layer
  owns: Account, FamilyGroup, FamilyMembership, Role, Permission,
        Auth/Credential, Session, ServiceSubscription
  |
  +-- 와글와글 (Wagle) — CORE_FAMILY realtime capability, never subscription-gated
  |
  +-- 마크포인트 (Markpoint) — FAMILY-owned optional service
```

Rows below marked "Implemented" are `CURRENT IMPLEMENTATION` evidence. They are
not claims that the approved Target contract for that area is complete.

## Layer 1 — 몽글 (Mongle family platform)

**Owns**: Account, FamilyGroup, FamilyMembership, Role, Permission, Service Subscription, and — per approved D2/D3 — Account credential (`아이디 + 플랫폼 비밀번호`) and persistent Account-scoped Session. **Not yet implemented**: the D2/D3 credential and Session capability has no code today; the contract is approved, the implementation is Wave 1 work.

| Sub-domain | Current code location | Status |
|---|---|---|
| Account | `backend/app/domains/family/models.py::Account` | Implemented (Foundation layer) |
| FamilyGroup | `backend/app/domains/family/models.py::FamilyGroup` | Implemented; Family-specific naming is approved by D1, not a pending question |
| Membership | `backend/app/domains/family/models.py::FamilyMembership` | Implemented |
| Role/Permission | `backend/app/domains/family/models.py::Role,Permission,RolePermission,MembershipRoleAssignment` | Implemented |
| Service Subscription | `backend/app/domains/family/models.py::ServiceSubscription` | Implemented |
| Legacy bridge | `backend/app/domains/family/models.py::LegacyIdentityMapping` | `CURRENT_STATE_EVIDENCE_NOT_TARGET_CONTRACT` — it exists in code today and that fact is not erased. Under approved D8 RESET it is **not** a Target login path, **not** a required cutover bridge, and **not** a bootstrapping prerequisite for new Accounts. New Accounts are created directly from the D2 credential flow. |
| Auth / Account credential | none | **Not implemented.** Contract approved by D2 (`아이디 + 플랫폼 비밀번호`, FamilyAdmin-provisioned independent Accounts). Wave 1 implementation scope. |
| Session | none | **Not implemented.** Contract approved by D3 (Account-scoped persistent Session aware of the whole `AuthorizedFamilySet`; expiry/refresh/revoke/device-unlink required). Wave 1 implementation scope. |
| Wagle PIN (local screen lock) | none | **Not implemented.** Contract approved by D3-PIN-SCOPE (`Account + Device`, optional, reset-not-recovery, never readable by FamilyAdmin, never blocks Push or other services). |

Cross-cutting: `service_outbox_events` (generic transactional outbox) sits at the platform layer conceptually — it is owner-agnostic by design (`owner_service` is a free string, no FK), meant to let any Service relay an event to any other Service without either one depending on the other's schema. Currently the only producer is MarkPoint and the only intended consumer is 와글와글, but the mechanism itself is platform infrastructure, not owned by either Service. Evidence: `backend/app/domains/service_outbox/models.py` docstring.

## Layer 2 — 와글와글 (Wagle: CORE_FAMILY realtime capability)

**Approved D5-A boundary:** Wagle is a **Core FamilyGroup capability**, not an optional service. Its realtime and Push delivery is never gated by `ServiceSubscription` absence, deactivation or suspension. Every FamilyGroup gets it on creation (`AUTO_ENABLE_ON_FAMILY_CREATION`).

**Owns**: Room, Participant, Message, Read State, Service Principal, Service Binding, Service Audit Log — all scoped to a FamilyGroup (`family_group_id` FK), never to a legacy Player. Per D1, Rooms, DMs, Participants, search, invite, read state and notifications never cross FamilyGroups.

**Approved D6 delivery boundary:** WebSocket foreground + Web Push background, durable DB and transactional Outbox as SSOT, at-least-once delivery with deduplication, ordering per `FamilyGroup + Room` (never global), one logical subscription per `Account + Device + Session` multiplexing the whole `AuthorizedFamilySet`, and per-FamilyGroup failure isolation. The Doran domain below is the durable-messaging **core candidate** for this contract; the realtime/Push transport is not built. See `MONGLE_REALTIME_MESSAGING_CONTRACT.md`.

**Physical naming:** the code uses `doran_*` / `doran`; the product name is 와글와글/Wagle. Renaming physical tables is a cosmetic, still-open naming question that D1–D8 do not decide and that blocks nothing.

| Sub-domain | Current code location | Status |
|---|---|---|
| Room (DIRECT/GROUP/SERVICE) | `backend/app/domains/doran/models.py::DoranRoom` | Implemented, already Group-scoped |
| Direct-pair uniqueness | `.../models.py::DoranDirectPair` | Implemented |
| Participant | `.../models.py::DoranParticipant` | Implemented, scoped to Membership (not Player) |
| Message | `.../models.py::DoranMessage` | Implemented, tombstone-pattern soft delete |
| Read State | `.../models.py::DoranParticipantReadState` | Implemented |
| Service Principal / Binding (for cross-service message relay, e.g. MarkPoint -> 와글와글) | `.../models.py::ServicePrincipal,DoranServiceBinding,DoranServiceAuditLog` | Implemented |
| API surface | `backend/app/domains/doran/router.py` (16 operations) | Implemented, tested (71 backend tests total incl. Doran-specific suites), zero frontend consumer (see `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md`) |
| Frontend | `frontend/src/platform/pages/DoranLanding.tsx` + `platform/doran/components/*` | UI components exist; render exclusively from static preview fixtures, not the real API |

**Legacy overlap to explicitly not carry forward as SSOT**: `chat_messages`/`ChatMessage` (pre-Doran, Player-to-Player 1:1 messaging) is a structurally separate, Player-scoped table that the Doran model's own docstring explicitly declines to reuse ("These tables deliberately do not reuse legacy `chat_messages`. Account, Service, and System message actors are structurally distinct."). Under the corrected framing, legacy `chat_messages` is reference-only UX material for "what a simple 1:1 chat looked like," not a component of 와글와글's target architecture.

## Layer 3 — 마크포인트 (Markpoint: FAMILY-owned optional service)

**Approved D5-B boundary:** Markpoint is a `FAMILY` service. Owner is `FamilyGroup`; human identity is `FamilyMembership`. A FamilyMember may request activation, FamilyAdmin approves or activates directly, and once `ACTIVE` every `ACTIVE` FamilyMembership gets default MEMBER access — **default access is not forced Mission participation**. Per-membership restriction is possible by explicit policy. ServiceAdmin is granted only by explicit assignment; the registrant is never automatically ServiceAdmin. **No `MarkpointParticipant` aggregate is introduced at this stage** — do not create one.

**Approved D5-C boundary:** Markpoint's automated notifications are published under a non-human 마크포인트 system actor represented by `ServicePrincipal` — never under a FamilyAdmin, ServiceAdmin or FamilyMember name. They are delivered only to an approved Wagle Room in the FamilyGroup where the source event occurred, are traceable to that source event, are deduplicated, and are not published at all for a FamilyGroup where Markpoint is `INACTIVE` or `SUSPENDED`.

**Owns** (today, all legacy-identity-scoped — `CURRENT IMPLEMENTATION` evidence): missions, mission templates, level tiers, daily points, deductions, cheer messages, feedback, notifications. See `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`. Under D8 RESET these legacy rows are never imported or backfilled into Target.

| Sub-domain | Current code location | Current owning identity | Target owning identity (per PM framing) |
|---|---|---|---|
| Mission | `backend/app/domains/mission/` | `players.id` | **D5-B approved:** FamilyGroup-owned, `FamilyMembership` identity. New Target records only — no legacy row conversion (D8) |
| Mission Template | `backend/app/domains/mission_template/` | `players.id` | same |
| Level Tier | `backend/app/domains/level_tier/` | `players.total_earned` (a Player-owned column) | same |
| Daily Point | `backend/app/domains/daily_point/` | `players.id` | same |
| Deduction | `backend/app/domains/deduction/` | `players.id` | same |
| Cheer | `backend/app/domains/cheer/` | none (date-keyed, not player-keyed at all) | Group (a cheer message is a whole-Group event today by its own schema shape) |
| Feedback | `backend/app/domains/feedback/` | `players.id` | same |
| Notification | `backend/app/domains/notification/` | `players.id` (nullable) | same |

Pure arithmetic/cycle logic is a **reusable business-logic** candidate, subject to verification. Mission transitions, approval, ledger/balance and notification need Target actor/scope/transaction/idempotency review. Two distinct things must not be confused: reusing existing **business logic** is approved in principle, while migrating existing **operational data** is prohibited by D8. A blind ownership-FK rewrite of legacy rows is not an approved transformation. See `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`.

## New-screen evidence addendum (0a–0g)

See `MONGLE_NEW_SCREENS_CONTRACT_IMPACT_REVIEW.md` §4 for full detail.
Evidence only, not a decision: the 0e (코드 참여) / 0f (승인 대기) / 0g (그룹
둘러보기) screens show Membership needs more than an active/inactive flag.
Candidate states surfaced: `PENDING`, `ACTIVE`, `REJECTED`, `SUSPENDED`,
`LEFT`, `CANCELLED`. Scenarios the eventual state machine must answer:
applicant vs. approval-authority actor split, cancel-while-pending,
re-apply after rejection/cancellation, invite-code expiry, and duplicate-code
submission. Note that "an Account active in one family while joining or pending
in another" is **not** an open question — D1 approves concurrent multiple
FamilyMemberships per Account outright. The remaining items are membership
state-machine detail for the relevant W1 task's Start Gate, not D1–D8 questions.

## Explicit non-domain: legacy `auth`/`player`/`admin` (PIN + username/password)

**Axis:** `CURRENT_STATE_EVIDENCE_NOT_TARGET_CONTRACT`.

This is reference material for UX and business-rule familiarity only, never a Mongle Auth/Session component. It is factually still the *only currently working* login mechanism in the repository, which is why it is not deleted yet — but under approved D8 RESET it is explicitly **not** a Target login path, **not** an automatic fallback, and **not** an SSOT. Legacy PINs and credentials are never converted into a platform password or a Wagle PIN. Legacy write freeze, read-only archiving and destructive retirement follow the separate PM-gated Cutover sequence in `MONGLE_MIGRATION_CUTOVER_BACKLOG.md`.
