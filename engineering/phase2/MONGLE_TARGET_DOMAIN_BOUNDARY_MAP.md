# MONGLE_TARGET_DOMAIN_BOUNDARY_MAP

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

Three-layer product structure per PM's corrected framing:

```text
몽글 (Mongle) — platform layer
  owns: Account, Group, Membership, Role, Permission, Auth, Session
  |
  +-- 와글와글 (Wagle-Wagle) — realtime messenger, a Service on Mongle
  |
  +-- 마크포인트 잔치 (MarkPoint Festival) — a Service on Mongle
```

## Layer 1 — 몽글 (Mongle platform)

**Owns**: Account, Group (currently Family-shaped, see PM_DECISION_REQUIRED in the Business Glossary), Membership, Role, Permission, Service Subscription. **Does not yet own**: Auth/Session (see Business Glossary — this is the one platform-layer capability with no current implementation at all).

| Sub-domain | Current code location | Status |
|---|---|---|
| Account | `backend/app/domains/family/models.py::Account` | Implemented (Foundation layer) |
| Group (Family) | `backend/app/domains/family/models.py::FamilyGroup` | Implemented, Family-specific |
| Membership | `backend/app/domains/family/models.py::FamilyMembership` | Implemented |
| Role/Permission | `backend/app/domains/family/models.py::Role,Permission,RolePermission,MembershipRoleAssignment` | Implemented |
| Service Subscription | `backend/app/domains/family/models.py::ServiceSubscription` | Implemented |
| Legacy bridge | `backend/app/domains/family/models.py::LegacyIdentityMapping` | Implemented — explicitly a *bridge from* legacy identity, not a Mongle-native Auth mechanism |
| Auth (Account-native) | none | **Not implemented** — see Business Glossary PM_DECISION_REQUIRED #2 |
| Session | none | **Not implemented** |

Cross-cutting: `service_outbox_events` (generic transactional outbox) sits at the platform layer conceptually — it is owner-agnostic by design (`owner_service` is a free string, no FK), meant to let any Service relay an event to any other Service without either one depending on the other's schema. Currently the only producer is MarkPoint and the only intended consumer is 와글와글, but the mechanism itself is platform infrastructure, not owned by either Service. Evidence: `backend/app/domains/service_outbox/models.py` docstring.

## Layer 2 — 와글와글 (realtime messenger Service)

**Owns**: Room, Participant, Message, Read State, Service Principal, Service Binding, Service Audit Log — all scoped to a Mongle Group (`family_group_id` FK), never to a legacy Player.

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

## Layer 3 — 마크포인트 잔치 (MarkPoint Festival Service)

**Owns** (today, all legacy-identity-scoped): missions, mission templates, level tiers, daily points, deductions, cheer messages, feedback, notifications. See `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md` for the full re-hosting analysis.

| Sub-domain | Current code location | Current owning identity | Target owning identity (per PM framing) |
|---|---|---|---|
| Mission | `backend/app/domains/mission/` | `players.id` | Membership (or Account) — not yet transformed |
| Mission Template | `backend/app/domains/mission_template/` | `players.id` | same |
| Level Tier | `backend/app/domains/level_tier/` | `players.total_earned` (a Player-owned column) | same |
| Daily Point | `backend/app/domains/daily_point/` | `players.id` | same |
| Deduction | `backend/app/domains/deduction/` | `players.id` | same |
| Cheer | `backend/app/domains/cheer/` | none (date-keyed, not player-keyed at all) | Group (a cheer message is a whole-Group event today by its own schema shape) |
| Feedback | `backend/app/domains/feedback/` | `players.id` | same |
| Notification | `backend/app/domains/notification/` | `players.id` (nullable) | same |

None of MarkPoint's business logic (mission state machine, point ledger arithmetic, level calculation, cycle-range math) is Mongle-platform-specific or Doran-specific — all of it is reusable regardless of what the owning identity FK is renamed/repointed to. See `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md` for the REUSE_LOGIC_ONLY inventory.

## Explicit non-domain: legacy `auth`/`player`/`admin` (PIN + username/password)

Per PM's correction, this is reference material for UX and business-rule familiarity only, not a Mongle Auth/Session component. It remains the *only currently working* login mechanism in the repository, which is why it cannot simply be deleted yet — see `MONGLE_MIGRATION_CUTOVER_GAP_REPORT.md`'s cutover-sequencing discussion.
