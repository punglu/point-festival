# MONGLE_TARGET_BUSINESS_GLOSSARY

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B: TARGET_MONGLE_ARCHITECTURE)

Frozen against `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED`, 2026-08-01).

몽글 is a new **family platform** owning Account, FamilyGroup, FamilyMembership, Role, Permission, Auth/Credential and Session (D1, D2, D3). 와글와글 (Wagle) is a **Core FamilyGroup capability**, never subscription-gated (D5-A). 마크포인트 (Markpoint) is a **`FAMILY`-owned optional service** whose human identity is FamilyMembership (D5-B). The legacy point-festival system (players/admin_auth/PIN/chat_messages/existing routes) is reference material only and, under D8 RESET, never an operational data source or fallback.

This glossary defines the target concepts. Where a target concept is **already implemented** by existing code (not legacy — the Foundation work registered as `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001`), that is stated with evidence. "Already implemented" describes code that exists, never that an approved decision is fully satisfied.

## Already-implemented target concepts (Foundation layer, not legacy)

These exist today, were built specifically as a forward-looking Account/Group/Role/Permission foundation (per the migration's own docstring: "Add Account, Family, membership, scoped Role, and Permission foundation"), and are evidence-confirmed to already match the shape PM just described for Mongle. They are **not** part of the legacy point-festival system being deprecated.

| Target term | Definition | Evidence it already exists |
|---|---|---|
| Account | Mongle's own identity — the thing a person authenticates as, independent of any specific service (MarkPoint, 와글와글) | `accounts` table, `Account` model — `backend/app/domains/family/models.py:6-11` |
| FamilyGroup | The organisation, communication and data-isolation boundary an Account belongs to, via FamilyMembership. Family-specific by approved D1 (`family_groups`, relationship enum mother/father/child/guardian/grandparent/other/unknown). Generalisation to a non-family Group model is **rejected**, not pending | `family_groups` table — `backend/app/domains/family/models.py:14-19` |
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
| Authentication (Account-native) | An Account's own first-class login credential: `아이디 + 플랫폼 비밀번호`, with FamilyAdmin able to provision independent Accounts and initial credentials inside its own FamilyGroup | **Contract approved (D2); not implemented.** Today an Account is reachable only indirectly through `LegacyIdentityMapping`, which requires a legacy `player_auth`/`admin_auth` login first, and there is no path to create or authenticate an Account on its own. Wave 1 builds the approved flow directly — not as a legacy bridge. |
| Session | The live, revocable artifact representing "this Account is logged in", Account-scoped and aware of the whole `AuthorizedFamilySet`, with expiry, refresh, revoke and per-device unlink | **Contract approved (D3); not implemented.** Today's JWTs are stateless, legacy-identity-shaped (`sub`=player_id or admin_auth.id, `role`=player/admin) and carry no Account/Membership/FamilyGroup reference; Account resolution happens after JWT verification via `resolve_current_account`. No `sessions` table, revocation or refresh rotation exists. Wave 1 scope. |
| Wagle PIN | An optional `Account + Device` local screen lock for the Wagle conversation screen — **not** authentication and **not** a credential | **Contract approved (D3-PIN-SCOPE); not implemented.** No shared or per-family PIN; not readable by FamilyAdmin; reset rather than recovered; never blocks background Push, unread counts or other services. |
| AuthorizedFamilySet | The server-derived set of all FamilyGroups in which the Session's Account holds an `ACTIVE` FamilyMembership | **Contract approved (D1/D3/D6); not implemented.** Distinct from `ActiveFamilyContext`, which is foreground screen convenience only and never a security boundary. |
| 마크포인트 잔치 as a Mongle service | MarkPoint's mission/point/level/deduction/cheer/feedback/notification business domain, re-hosted so its ownership foreign keys point at Mongle Group/Membership instead of legacy `players` | **Business logic exists and is reusable (see `MONGLE_MARKPOINT_ON_MONGLE_CONTRACT.md`); the persistence layer does not yet point at Mongle identities.** Every `missions`/`daily_points`/`deductions`/`cheer_messages`/`feedbacks`/`notifications` row's owning FK is `player_id -> players.id`, a purely legacy identity, with zero column referencing `family_membership_id` or `account_id` anywhere in these tables. |

## Formerly-open items — now resolved by the approved Decision Freeze

Items 1 and 2 below were `PM_DECISION_REQUIRED` when this glossary was written.
They are **closed** by `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED`,
2026-08-01). The original options are retained as `VALID_HISTORICAL_REFERENCE`
only and must not be reopened.

1. **"Group" vs "Family" — RESOLVED by D1.** 몽글 is a **family platform**, not a
   generic Group platform. The physical names `family_groups` and
   `family_memberships` are approved and retained (`KEEP_AS_IS`). A generic
   `groups`/`group_memberships`/`group_type` model is **not** in the Target
   contract and must not be introduced. One Account may hold multiple
   FamilyMemberships; `FamilyGroup` is the organisation, communication and
   data-isolation boundary.
2. **Account-native Auth/Session — RESOLVED by D2, D3 and D3-PIN-SCOPE.** The
   approved model is closest to historical option (a) but is not identical to
   it, so read the approved contract, not the option:
   - Platform login is **아이디/username + 플랫폼 비밀번호**. Email and phone are
     **not required**.
   - `FamilyAdmin` may create **independent Accounts** and issue initial
     credentials for members of its own FamilyGroup. Such an Account is a full
     independent Account, never a child profile of the admin's Account.
   - Session is **Account-scoped and persistent**, aware of the entire
     `AuthorizedFamilySet` rather than one family, and supports expiry,
     refresh, revoke and per-device unlink.
   - The PIN is **not** authentication. It is an optional `Account + Device`
     local screen lock for the Wagle conversation screen only: no shared or
     per-family PIN, not readable by FamilyAdmin, reset rather than recovered,
     and it never blocks background Push or other services.
   - Historical option (b) (email/phone/OAuth as the required credential) and
     option (c) (creator-credential + invite-token-only members) are **not**
     the approved model. Additional optional signup surfaces seen in the 0b
     screen evidence are a separate, deferred UI-task question.
3. **Are the seeded Role/Permission codes final?** — **still open**, classified
   `REQUIRES_PM_REVIEW`, `NON_BLOCKING`. D4 approves the *structure*
   (FamilyAdmin and ServiceAdmin are separate, FamilyMembership-scoped roles;
   service work authority requires explicit ServiceAdmin assignment; default
   deny; last-admin protection; audit). D4 does **not** re-confirm the specific
   seeded code strings (`owner`/`admin`/`member`/`restricted_member` for FAMILY
   scope; `participant`/`mission_manager`/`point_admin` for `markpoint`;
   `participant`/`room_admin` for `doran`). These were seeded by the
   already-PM-reviewed `PHASE1-ACCOUNT-FAMILY-RBAC-CONTRACT-001` migration and
   remain the working baseline; renaming any of them later is a real migration,
   so the Wave 1 RBAC task should confirm them at its Start Gate rather than
   assume or silently change them.
