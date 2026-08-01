# Implementation Backlog

> Recalculated against `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED` /
> `FROZEN`, 2026-08-01). Wave assignments come from
> `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`, whose Wave column — not the `W<n>`
> fragment inside a task ID — is authoritative.

## Status vocabulary

| Status | Meaning |
|---|---|
| `DONE` | completed and evidenced |
| `READY_FOR_IMPLEMENTATION` | frozen decisions cover it, its dependencies are satisfied, and repository evidence shows it can actually be started |
| `BLOCKED_BY_DEPENDENCY` | contract is frozen but a preceding task must land first |
| `DEFERRED_TO_RELEVANT_TASK_START_GATE` | needs a named policy decision (`D6-P*` or a service-specific policy) before it may start |
| `SUPERSEDED_BY_APPROVED_DECISION` | an approved decision removed this work; retained as a historical record, never implemented |
| `REFERENCE_ONLY` | evidence or background, not deliverable work |

`READY_FOR_IMPLEMENTATION` means "may pass its own Start Gate and begin", not
"authorized to skip one". No task is `PM_DECISION_REQUIRED` because of D1–D8.

Every task must declare actor/precondition, FE/BE/DB/API/event/migration/RBAC/
observability scope, owned files, a single owner for any shared file,
out-of-scope boundaries, rollback, and Target Product / Migration Guard test
linkage in its own handoff before implementation. Tests follow
`agent-system/qa/TEST_POLICY.md`; the coverage denominator is the Target product
requirement surface.

## Wave 0 — contracts

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W0-DECISION-CONTRACTS-001 | 0 | `DONE` | approved, frozen Target contract | D1–D8 | Frozen Decision Contract plus the recalculated planning set: this backlog, the Epic/Feature decomposition, the Wave plan, the Reset/Cutover backlog and the DoD/Test matrix. Evidence: `MONGLE_APPROVED_DECISIONS_FREEZE_AND_DECOMPOSITION_REPORT.md` |

## Wave 1 — Account, credential, Session, family context, scoped RBAC

> **Backend slice delivered 2026-08-01** by execution bundle
> `MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001`. The five backend rows below are
> `DONE` with 33/33 new tests and 104/104 suite-wide passing against an isolated
> disposable Postgres; evidence in
> `agent-system/qa/MONGLE-W1-AUTONOMOUS-IMPLEMENTATION-001.md`. `DONE` here means
> implemented and self-tested — independent QA has **not** run yet.
>
> The five FE rows still marked `BLOCKED_BY_DEPENDENCY` now have their **backend**
> dependency satisfied, but their status is deliberately left unchanged: each
> also carries its own unresolved design condition (the 0c "나중에 하기" limited
> mode, 0d duplicate-name handling, 0e invalid/expired/already-member states, 0f
> rejected-state screen). Promoting them is their own Start Gate's decision, not
> this bundle's.

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W1-ACCOUNT-CREDENTIAL-001 | 1 | `DONE` | login with 아이디 + 플랫폼 비밀번호 | D2 | Account credential store and login/logout; email and phone are **not** required; password hashing and failure handling; no legacy credential conversion (D8). Tests: login success/failure, duplicate identifier, password reset |
| MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001 | 1 | `DONE` | FamilyAdmin provisions an independent Account for a family member | D2, D4 | Issue an **independent** Account plus initial credential, scoped strictly to the admin's own FamilyGroup; initial-password reset and family-access recovery. Explicit denials: reading a member's password or PIN, impersonation, cross-family issuance, treating the Account as a child profile. Tests: issuance boundary, cross-family deny, credential-read deny |
| MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001 | 1 | `DONE` | persistent Session and family context separation | D1, D3, D7 | Account-scoped persistent Session with expiry, refresh, revoke and per-device unlink; server-derived `AuthorizedFamilySet`; `ActiveFamilyContext` as convenience state only; Push authority withdrawn on logout/suspension/revoke/unlink. Tests: restart persistence, expiry, refresh, revoke, device unlink, multi-membership context, context-vs-authorized-set separation |
| MONGLE-W1-SCOPED-RBAC-001 | 1 | `DONE` | FamilyMembership-scoped platform/family/service authorization | D4 | Role bindings with default deny; FamilyAdmin and ServiceAdmin separated; FamilyAdmin may self-assign ServiceAdmin but the assignment must exist; role changes audited; roles end on membership leave/suspension; last-admin protection. **Start Gate:** confirm the seeded role/permission code strings (`REQUIRES_PM_REVIEW`, non-blocking). Tests: default deny, cross-family deny, admin separation, last-admin protection, audit record |
| MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001 | 1 | `DONE` | family-scoped route and API authorization | D7 | `/families/{familyId}/...` for family-owned surfaces and `/me/...` for personal ones; the server never trusts a URL or client `familyId` and revalidates Session, membership and status, owner scope or entitlement, role/permission and resource ownership. Tests: substituted `familyId` deny, revoked-membership stale-route deny, personal/family route separation, multi-tab isolation |
| MONGLE-W1-ONBOARDING-INTRO-UI-001 | 1 | `BLOCKED_BY_DEPENDENCY` | pre-login onboarding carousel (0a/0a-2/0a-3) | MONGLE-W1-ACCOUNT-CREDENTIAL-001 | static intro screens with existing-login and signup exits. Pre-login routes are not family-scoped, so D7 does not fix their paths |
| MONGLE-W1-ACCOUNT-SIGNUP-UI-001 | 1 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | account creation intake (0b) | MONGLE-W1-ACCOUNT-CREDENTIAL-001; per-credential v1 scope decision | The D2 baseline (아이디 + 비밀번호) is approved and buildable. The 0b screen's **additional optional** surfaces (email+password, phone+SMS, Google, Apple) each need a `V1_REQUIRED`/`V1_OPTIONAL`/`DEFERRED`/`REFERENCE_ONLY` call at this task's Start Gate. Verification, consent and duplicate/failure states are undefined in the source and must be designed, not copied |
| MONGLE-W1-FAMILY-SELECTION-UI-001 | 1 | `BLOCKED_BY_DEPENDENCY` | post-signup no-family hub (0c) | MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001 | family-existence branch; auto-select on exactly one membership and a selection screen on several; the "나중에 하기" limited-mode route is undefined in the source and must be designed |
| MONGLE-W1-FAMILY-CREATION-UI-001 | 1 | `BLOCKED_BY_DEPENDENCY` | create a new family (0d) | MONGLE-W1-SCOPED-RBAC-001 | creator becomes FamilyAdmin per D4; the creator's self-selected **relationship** (including 자녀) is independent of that role — surface copy must not imply otherwise; duplicate-name handling is undefined in the source |
| MONGLE-W1-FAMILY-CODE-JOIN-UI-001 | 1 | `BLOCKED_BY_DEPENDENCY` | join by invite code (0e) | MONGLE-W1-SCOPED-RBAC-001, MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001 | code issuance/validation authority per D4; invalid, expired and already-member states are undefined in the source |
| MONGLE-W1-MEMBERSHIP-PENDING-UI-001 | 1 | `BLOCKED_BY_DEPENDENCY` | approval-wait state (0f) | MONGLE-W1-SCOPED-RBAC-001 | approval authority per D4; membership state machine per `MONGLE_TARGET_DOMAIN_BOUNDARY_MAP.md`; the rejected-state screen is undefined in the source. Concurrent membership in several families is approved by D1 and is not an open question |
| MONGLE-W1-FAMILY-DISCOVERY-UI-001 | 1 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | search/discover joinable families (0g) | discovery-privacy decision | Needs a Start Gate decision on public directory versus invite-only/contact-scoped discovery, and on browse permission for a session with no active membership. The PM-suggested 0c→0g entry card is direction only — do not add it unilaterally |
| MONGLE-W1-AUTH-BRAND-INTEGRATION-001 | 1 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | Mongle wordmark on auth/onboarding surfaces | explicit PM asset approval | text/wordmark asset only, never the character; design may still change, so a separate explicit PM approval is required at implementation time |

## Wave 2 — Wagle durable messaging foundation

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W2-WAGLE-DURABLE-COMMAND-001 | 2 | `BLOCKED_BY_DEPENDENCY` | idempotent durable send command and history | Wave 1; D4, D6 | Durable send with `client_message_id` idempotency returning the existing result on retry; room and participant rules; message history query. **No user-facing `DELIVERED`** |
| MONGLE-W2-WAGLE-TRANSACTIONAL-OUTBOX-001 | 2 | `BLOCKED_BY_DEPENDENCY` | atomic message + Outbox commit | MONGLE-W2-WAGLE-DURABLE-COMMAND-001; D6 | Message persistence and Outbox enqueue in **one transaction**; sender success reported only after commit; a later realtime or Push failure never loses the message or reverses success. **Start Gate:** verify whether the current implementation already shares one transaction. Tests: forced post-persist failure leaves no divergence |
| MONGLE-W2-WAGLE-ORDERING-CURSOR-001 | 2 | `BLOCKED_BY_DEPENDENCY` | room-scoped ordering, cursor and read state | MONGLE-W2-WAGLE-DURABLE-COMMAND-001; D6 | Monotonic order per `FamilyGroup + Room` via `room_sequence` or equivalent; forward-only read cursor; per-family unread isolation. **Global ordering must not be implemented** |
| MONGLE-W2-WAGLE-ROOM-LIST-READ-MODEL-001 | 2 | `BLOCKED_BY_DEPENDENCY` | batch room list with preview and unread | MONGLE-W2-WAGLE-ORDERING-CURSOR-001 | One call returning rooms plus last-message preview plus unread count; today `list_rooms` returns bare rows. Response shape is this task's design work |

## Wave 3 — Wagle realtime, PWA Push, recovery, PIN

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W2-WAGLE-REALTIME-001 | 3 | `BLOCKED_BY_DEPENDENCY` | realtime dispatcher and WebSocket gateway | Wave 2; D6 | Outbox consumer/dispatcher and WebSocket gateway; one **logical** subscription per `Account + Device + Session` while tolerating multiple concurrent physical sockets, each with its own connection ID and server-side lifecycle and dedup. At-least-once with deduplication. Retry, duplicate and revoke tests |
| MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | PWA Web Push subscription and revocation | Wave 2; D6; **D6-P1** | Subscription bound to Account and device/PWA installation; revoked on logout, Account suspension, Session revoke, device unlink and Account switch. Payload disclosure level is `D6-P1` and must be decided before this task starts |
| MONGLE-W3-WAGLE-RECONNECT-RESUME-001 | 3 | `BLOCKED_BY_DEPENDENCY` | reconnect, resume and recovery | MONGLE-W2-WAGLE-REALTIME-001; D6 | Client-held cursor or resume token; on reconnect the server returns missed events and both sides deduplicate. Survives reconnect, server restart, device sleep, PWA relaunch and Push loss with no loss and no duplicate display. Push is never treated as guaranteed delivery or SSOT |
| MONGLE-W3-WAGLE-MULTIFAMILY-SUBSCRIPTION-001 | 3 | `BLOCKED_BY_DEPENDENCY` | one logical subscription across all authorized families | MONGLE-W2-WAGLE-REALTIME-001; D1, D6 | Multiplex the server-derived `AuthorizedFamilySet`; `ActiveFamilyContext` never suppresses another authorized family; arbitrary client family subscription denied; membership approval and revocation update the subscription incrementally, revoking only that family |
| MONGLE-W3-WAGLE-FAILURE-ISOLATION-001 | 3 | `BLOCKED_BY_DEPENDENCY` | per-family and per-device failure isolation | MONGLE-W2-WAGLE-REALTIME-001; D6 | Outbox, cursor, read state, unread count, retry and failure records isolated per FamilyGroup; one family's, device's or event's failure never blocks another's delivery |
| MONGLE-W3-WAGLE-PIN-LOCK-001 | 3 | `BLOCKED_BY_DEPENDENCY` | optional Wagle PIN screen lock | Wave 1; D3-PIN-SCOPE | `Account + Device` local lock on the conversation screen; one personal PIN per device across all that account's families; no shared or per-family PIN; not readable by FamilyAdmin; **reset, never recovery**; failure never logs the platform out or blocks other services; while locked, Push and unread counts continue but sensitive bodies stay hidden |
| MONGLE-W3-WAGLE-PUSH-DEEPLINK-AUTHZ-001 | 3 | `BLOCKED_BY_DEPENDENCY` | authorized Push deep-link navigation | MONGLE-W3-WAGLE-PUSH-SUBSCRIPTION-001; D6, D7 | Opening a Push revalidates Session, Account state, membership, family scope and room/resource permission, lands on the event's own family, and shows an inaccessible state rather than data when authority is gone |
| MONGLE-W3-WAGLE-NOTIFICATION-SETTINGS-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | per-room mute and notification settings | **D6-P2** | No default is assumed. Whatever policy is chosen, per-message server records and ordering are preserved |
| MONGLE-W3-WAGLE-PUSH-BUNDLING-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | Push bundling and foreground suppression | **D6-P3** | Includes whether an open foreground room suppresses device Push |
| MONGLE-W3-WAGLE-READ-DISPLAY-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | read-state display | **D6-P4** | Durable read state is already contract; only its user-facing presentation is deferred. A user-facing `DELIVERED` state requires separate PM approval and is out of scope |
| MONGLE-W3-WAGLE-PRESENCE-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | online status and last-seen | **D6-P5** | Disclosure is undecided; do not infer a default from legacy behaviour |
| MONGLE-W3-WAGLE-MESSAGE-MUTATION-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | message edit and delete | **D6-P6** | The current tombstone delete pattern is evidence, not an approved edit policy |
| MONGLE-W3-WAGLE-RETENTION-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | message and system-event retention | **D6-P7** | Retention interacts with the Legacy archive rules in Wave 7; decide before building |
| MONGLE-W3-WAGLE-OFFLINE-QUEUE-001 | 3 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | offline outbound queue | **D6-P8** | Whether v1 includes it at all is undecided. `PENDING`/`SENT`/`FAILED` client states are already contract regardless |

## Wave 4 — service ownership, activation and Markpoint access

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001 | 4 | `BLOCKED_BY_DEPENDENCY` | Markpoint family-service access and activation policy | Wave 1; D5-A, D5-A3, D5-B | **Replaces MONGLE-W3-MARKPOINT-PARTICIPANT-001.** Family-owned service instance; FamilyMember request → FamilyAdmin approval, plus FamilyAdmin direct activation; `ACTIVE` membership default access that is **not** forced Mission participation; explicit per-member restriction; explicit ServiceAdmin assignment only; registrant never auto-admin; `INACTIVE`/`ACTIVE`/`SUSPENDED` states with platform-only suspension release. **No `MarkpointParticipant` aggregate.** Tests: request/approve/reject, direct activation, default access, restriction, registrant-not-admin, non-admin work deny |
| MONGLE-W4-MARKPOINT-SYSTEM-EVENT-RELAY-001 | 4 | `BLOCKED_BY_DEPENDENCY` | Markpoint → Wagle system notifications | MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001, MONGLE-W2-WAGLE-REALTIME-001; D5-C | `ServicePrincipal` non-human 마크포인트 actor, never a human name; FamilyGroup and room binding authorization with cross-family delivery denied; source-event traceability; idempotent relay with no duplicate publication; no new events while the service is `INACTIVE`/`SUSPENDED`; human and system messages distinguished in UI and audit. `player_id` is never auto-converted to `service_principal_id` |
| MONGLE-SERVICE-DEFINITION-POLICY-001 | 4 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | per-service owner scope, registrant, activation, access, retention and Push policy | D5-A1/A2/A3; the named service's own policy decision | D5-A1/A2/A3 approve the **framework**, not each service's specifics. No physical table is inferred from a logical term |
| MONGLE-PERSONAL-SERVICE-OWNERSHIP-001 | 4 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | Account-owned personal service stays private | D5-A1; the named personal service's policy | Account identity; FamilyAdmin access denied; survives family switch and leave; Account-targeted Push. Needs a concrete personal service to be approved first |
| MONGLE-FAMILY-SERVICE-OWNERSHIP-001 | 4 | `BLOCKED_BY_DEPENDENCY` | family-owned records outlive the registrar | Wave 1; D5-A1, D5-B | FamilyGroup ownership regardless of registrant; FamilyMembership identity; cross-family isolation; registrant leave, suspension or Account deletion never deletes the service or its records |
| MONGLE-FAMILY-SERVICE-REGISTRATION-001 | 4 | `BLOCKED_BY_DEPENDENCY` | permitted member request, self-activation or admin-only flow | Wave 1; D4, D5-A2, D5-A3 | Request/approve/reject/deny flows per declared policy; **no automatic ServiceAdmin grant**; Registrant, Owner, User, ServiceAdmin and ServicePrincipal kept distinct |
| MONGLE-SERVICE-ACCESS-POLICY-001 | 4 | `DEFERRED_TO_RELEVANT_TASK_START_GATE` | default access and role/permission for a concrete service | D4, D5-A3, D5-B; that service's access decision | Positive and negative authorization, ServiceAdmin scope, Push revalidation. Markpoint's own answer is already frozen by D5-B and lives in MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001 |
| MONGLE-SERVICE-OWNERSHIP-LIFECYCLE-001 | 4 | `BLOCKED_BY_DEPENDENCY` | registrar leave, admin change and family dissolution | Wave 1; D5-A1/A2, D5-B, D8 | Retention and revocation semantics; archive/export/delete decisions; roles end on membership leave or suspension. Under D8 this is fresh-start lifecycle behaviour, **not** Legacy migration |

## Wave 5 — Markpoint product on Target ownership

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W5-MARKPOINT-TARGET-OWNERSHIP-001 | 5 | `BLOCKED_BY_DEPENDENCY` | Markpoint Target ownership and fresh schema transition | MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001; D5-B, D8 | **Replaces MONGLE-W3-MARKPOINT-OWNERSHIP-ADAPTER-001**, whose legacy backfill/adapter framing conflicts with D8. New operational records are created under `FamilyMembership`/`FamilyGroup` target ownership; **no legacy player-data backfill, migration or reconciliation**; existing mission/point/level business logic is reused **after verification**; test and fixture data stays separate from operational data. Explicitly out of scope: reading legacy rows for import, converting `player_id`, and importing any opening balance |
| MONGLE-W4-MARKPOINT-MISSION-LEDGER-001 | 5 | `BLOCKED_BY_DEPENDENCY` | mission, approval and point-ledger workflow | MONGLE-W5-MARKPOINT-TARGET-OWNERSHIP-001; D4, D5-B, D7 | Mission lifecycle and approval by explicitly assigned ServiceAdmin; transactional point ledger and balance; level/title and reward. Authorization, transaction-integrity and approval-authority tests |

## Wave 6 — Target product UI

| Task ID | Wave | Status | Product outcome | Dependencies | Work / DoD |
|---|---|---|---|---|---|
| MONGLE-W5-TARGET-UI-001 | 6 | `BLOCKED_BY_DEPENDENCY` | Target product journeys on real APIs | frozen Wave 1–5 contracts per slice | Accessible, responsive FE slices plus Target E2E, including multi-family journeys and Push deep-link context switching. **Start Gate:** the consumed backend contract must be reachable — no slice may claim integration while rendering from static preview fixtures |

## Wave 7 — fresh cutover and Legacy retirement

Owned by `MONGLE_MIGRATION_CUTOVER_BACKLOG.md`. All rows are `D8 RESET`
fresh-start validation, and none may begin before Wave 6 Target journey E2E
passes.

## Superseded by approved decisions

Retained as historical planning records. **Do not implement.** Their existence
does not erase the current-state fact that a legacy bridge exists in code today.

| Task ID | Status | Superseding decision | Replacement |
|---|---|---|---|
| MONGLE-W3-MARKPOINT-PARTICIPANT-001 | `SUPERSEDED_BY_APPROVED_DECISION` | D5-B — no separate participant aggregate at this stage | MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001 |
| MONGLE-W3-MARKPOINT-OWNERSHIP-ADAPTER-001 | `SUPERSEDED_BY_APPROVED_DECISION` | D8 RESET — its legacy backfill/adapter framing is prohibited | MONGLE-W5-MARKPOINT-TARGET-OWNERSHIP-001 |
| MONGLE-W6-IDENTITY-MAPPING-001 | `SUPERSEDED_BY_APPROVED_DECISION` | D8 RESET | MONGLE-W6-EMPTY-TARGET-SCHEMA-001 |
| MONGLE-W6-GROUP-MEMBERSHIP-001 | `SUPERSEDED_BY_APPROVED_DECISION` | D8 RESET | MONGLE-W6-NEW-FAMILY-ONBOARDING-001 |
| MONGLE-W6-MARKPOINT-LEDGER-001 | `SUPERSEDED_BY_APPROVED_DECISION` | D8 RESET | MONGLE-W6-INITIAL-LEDGER-INVARIANT-001 |
| MONGLE-W6-HISTORY-RETENTION-001 | `SUPERSEDED_BY_APPROVED_DECISION` | D8 RESET | MONGLE-W6-LEGACY-READONLY-BACKUP-001 |

## Epic mapping against the previous revision

| Previous | Now |
|---|---|
| E1 몽글 identity | E1 몽글 platform identity, with credential and route-authorization split into their own tasks |
| E2 와글와글 (single epic) | E2 durable messaging + E3 delivery and recovery |
| E3 Markpoint identity | dissolved — D5-B removes the participant-lifecycle question; access/activation moves to E4 |
| E4 Markpoint product | E5 |
| E5 product UI | E6, with auth/onboarding slices delivered inside Wave 1 |
| E6 cutover | E7, redefined as fresh cutover and retirement rather than migration |
