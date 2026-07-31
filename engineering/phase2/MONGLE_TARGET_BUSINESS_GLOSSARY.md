# MONGLE_TARGET_BUSINESS_GLOSSARY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B: TARGET_MONGLE_ARCHITECTURE)

PM correction (2026-07-31): Mongle is a new platform owning Account/Group/Membership/Role/Permission/Auth/Session. 와글와글 is a new realtime messenger running on Mongle. 마크포인트 잔치 is a new service built on Mongle's user/group/permission/session structure. The legacy point-festival system (players/admin_auth/PIN/chat_messages/existing routes) is reference material only, not the SSOT for any of this.

This glossary defines the target concepts. Where a target concept is **already implemented** by existing code (not legacy — the Foundation work registered as `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001`, PM-reviewed and built before this correction), that is stated explicitly with evidence, not re-invented. Where a target concept requires a naming/scope decision this task cannot make unilaterally, it is marked `PM_DECISION_REQUIRED`.

## Already-implemented target concepts (Foundation layer, not legacy)

These exist today, were built specifically as a forward-looking Account/Group/Role/Permission foundation (per the migration's own docstring: "Add Account, Family, membership, scoped Role, and Permission foundation"), and are evidence-confirmed to already match the shape PM just described for Mongle. They are **not** part of the legacy point-festival system being deprecated.

| Target term | Definition | Evidence it already exists |
|---|---|---|
| Account | Mongle's own identity — the thing a person authenticates as, independent of any specific service (MarkPoint, 와글와글) | `accounts` table, `Account` model — `backend/app/domains/family/models.py:6-11` |
| Group | The tenant/organizational boundary an Account belongs to. **Currently implemented specifically as "Family"** (`family_groups`, relationship enum mother/father/child/guardian/grandparent/other/unknown) — see `PM_DECISION_REQUIRED` #1 below on whether "Group" stays Family-specific or generalizes | `family_groups` table — `backend/app/domains/family/models.py:14-19` |
| Membership | An Account's participation record in one Group | `family_memberships` table — `.../models.py:22-35` |
| Role | A named permission bundle, scoped either to the whole Group (`FAMILY` scope_type) or to one specific Service within the Group (`SERVICE` scope_type + `service_code`) | `roles` table — `.../models.py:38-51` |
| Permission | An individual, dot-namespaced capability code (e.g. `family.members.manage`, `markpoint.missions.manage`, `doran.messages.send`) | `permissions` table — `.../models.py:54-58` |
| Role-Permission binding | Many-to-many join between Role and Permission | `role_permissions` — `.../models.py:62-65` |
| Membership-Role assignment | A revocable (not deletable) grant of one Role to one Membership | `membership_role_assignments` — `.../models.py:68-75` |
| Service Access / Service Subscription | A Group's own enablement record for a named service (`markpoint`, `doran`) — independent of any specific Role or Binding | `service_subscriptions` — `.../models.py:78-89` |
| Realtime Messaging (와글와글) domain model | Room (DIRECT/GROUP/SERVICE), Participant, Message, Read State, Service Principal, Service Binding — all scoped to Group, not to legacy Player | `backend/app/domains/doran/models.py` (full domain, see `MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md`) |
| Cross-service event relay primitive | A generic, owner-agnostic transactional outbox any service can enqueue an event into, for eventual relay to another service (today: MarkPoint mission-completion -> 와글와글 SERVICE room, though the relay worker itself does not exist yet — see Gap Report) | `service_outbox_events` — `backend/app/domains/service_outbox/models.py` |

## Not yet implemented — genuinely new target concepts

| Target term | Definition | Status |
|---|---|---|
| Authentication (Account-native) | An Account's own, first-class login credential and verification mechanism | **Does not exist.** Today an Account can only ever be reached indirectly, through `LegacyIdentityMapping`, which requires a legacy `player_auth`/`admin_auth` login to happen first. There is no path to create or authenticate an Account on its own. See `PM_DECISION_REQUIRED` #2. |
| Session | The live, revocable artifact representing "this Account is currently logged in," and its lifecycle (issuance, refresh, expiry, revocation) | **Does not exist as a first-class concept.** Today's JWTs are stateless, legacy-identity-shaped (`sub`=player_id or admin_auth.id, `role`=player/admin), and carry no reference to Account/Membership/Group at all — Account resolution happens *after* JWT verification, per-request, via `resolve_current_account`. A Mongle-native Session concept (e.g. a `sessions` table for revocation, refresh-token rotation) does not exist. See `PM_DECISION_REQUIRED` #2. |
| 마크포인트 잔치 as a Mongle service | MarkPoint's mission/point/level/deduction/cheer/feedback/notification business domain, re-hosted so its ownership foreign keys point at Mongle Group/Membership instead of legacy `players` | **Business logic exists and is reusable (see `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`); the persistence layer does not yet point at Mongle identities.** Every `missions`/`daily_points`/`deductions`/`cheer_messages`/`feedbacks`/`notifications` row's owning FK is `player_id -> players.id`, a purely legacy identity, with zero column referencing `family_membership_id` or `account_id` anywhere in these tables. |

## PM_DECISION_REQUIRED items

1. **Should "Group" remain a Family-specific concept, or generalize?** Evidence: the existing, already-approved implementation is concretely Family-shaped (`family_groups.name`, `family_memberships.relationship` CHECK-constrained to `mother/father/child/guardian/grandparent/other/unknown`). PM's own new instruction describes Mongle as owning a generic "Group" concept. Recommendation (not a decision): given Mongle's actual product is a family-communication platform, keeping "Group" concretely specialized as "Family" is very likely the intended reading of PM's own wording, and no evidence suggests a non-family Group use case is planned — but this task will not silently assume that. If PM confirms Family-only, the existing physical names (`family_groups`, `family_memberships`) can be `KEEP_AS_IS`; if PM wants a domain-agnostic Group that Family is merely one type of, that is a `TRANSFORM` (rename + a `group_type` discriminator), not a `KEEP_AS_IS`.
2. **What is the Account-native Auth/Session model?** No current code answers this. Candidate options, presented for PM selection, not decided here:
   - (a) Generalize `admin_auth`'s username/password pattern into the one universal Account credential, with today's PIN flow becoming a *convenience/quick-unlock* layer for an already-authenticated Session, not the primary credential.
   - (b) Introduce email/phone + password or an external IdP (OAuth) as the Account credential, keeping PIN entirely as a device-local, per-Membership quick-switch mechanism (closest to preserving today's UX while making Account the real security boundary).
   - (c) Some hybrid where the Group's first Account (the creator/Owner) uses a real credential, and subsequently-invited Memberships are provisioned via an invite-token flow rather than self-registration.
   No option is selected by this task. This is the single largest open architectural item blocking a genuine Auth/Session contract.
3. **Are the already-implemented Role/Permission codes (`owner`/`admin`/`member`/`restricted_member` for FAMILY scope; `participant`/`mission_manager`/`point_admin` for `markpoint`; `participant`/`room_admin` for `doran`) final for the target architecture, or does the corrected Mongle framing require different names/splits?** These were seeded by an already-PM-reviewed migration (`PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001`), so this task treats them as the current approved baseline, not as something requiring re-invention — but flags that PM has not been asked to re-confirm them under this corrected framing specifically, and may wish to.
