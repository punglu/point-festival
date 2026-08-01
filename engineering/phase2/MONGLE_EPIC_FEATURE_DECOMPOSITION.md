# Epic / Feature Decomposition

> Recalculated against `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED` /
> `FROZEN`, 2026-08-01). **No epic or feature below is `PM_DECISION_REQUIRED` on
> account of D1–D8.** Remaining deferrals are `D6-P1`–`D6-P8` and named
> future-service policies, both resolved at the relevant task's own Start Gate.
> Task-level status, ownership and sequencing live in
> `MONGLE_IMPLEMENTATION_BACKLOG.md` and `MONGLE_DEPENDENCY_AND_WAVE_PLAN.md`;
> this document owns the epic/feature shape only.

An approved decision authorizes planning and, once a task's own Start Gate
passes, implementation. It is never evidence that anything is built.

## Epics

| Epic | Features | Vertical outcome | Frozen decision basis |
|---|---|---|---|
| E0 Target contracts | approved decision freeze, domain/route/event/test contracts, recalculated plan | a frozen build boundary every task can cite | D1–D8 |
| E1 몽글 platform identity | Account credential, FamilyAdmin-provisioned Account, persistent Session, AuthorizedFamilySet vs ActiveFamilyContext, scoped RBAC, family-scoped route authorization | login → Session → family context → permitted family-scoped route | D1, D2, D3, D4, D7 |
| E2 와글와글 durable messaging | idempotent durable send command, Room-scoped ordering/cursor/read state, transactional Outbox, room-list read model | send → single-transaction DB+Outbox commit → durable history and cursor | D1, D4, D6, D7 |
| E3 와글와글 delivery and recovery | WebSocket gateway, PWA Web Push, reconnect/resume, multi-family logical subscription, per-family failure isolation, Wagle PIN lock, Push deep-link authorization | authorized delivery across every active family, recoverable from the DB after any transport loss | D1, D3, D3-PIN-SCOPE, D6, D7 |
| E4 service ownership and activation | owner scope declaration, registration authority, activation policy framework, Markpoint access/activation, Markpoint system actor | a family activates a service and only explicitly assigned admins operate it | D5-A, D5-A1, D5-A2, D5-A3, D5-B, D5-C |
| E5 마크포인트 product on Target ownership | Target ownership foundation, mission workflow, approval, point ledger/balance, level/title, reward | a FamilyMembership completes a mission and the approved result lands in the new ledger | D4, D5-B, D7, D8 |
| E6 Target product UI | auth/onboarding slices, family selection/creation/join, Wagle screens, Markpoint member and admin screens, multi-family journeys, accessibility/responsive | approved end-to-end Target journeys across multiple families | E1–E5 frozen backend contracts |
| E7 fresh cutover and Legacy retirement | empty-schema validation, seed/fixture separation, new-family bootstrap, opening-ledger invariant, Legacy write freeze, read-only archive, cutover, post-cutover verification, PM-gated retirement | a verified fresh Target start with Legacy safely frozen and archived | D8 |

Note the epic renumbering against the previous revision: the former single "E2
와글와글" epic is split into **E2 durable messaging** and **E3 delivery and
recovery**, because D6 makes durability and transport separately testable
concerns with different owners and different deferred policies. The former "E3
Markpoint identity" epic is dissolved — D5-B removes the participant-lifecycle
question that justified it. See the mapping table in
`MONGLE_IMPLEMENTATION_BACKLOG.md`.

## E1 feature detail

| Feature | Vertical outcome | Frozen basis |
|---|---|---|
| Account credential | a person logs in with 아이디 + 플랫폼 비밀번호; email and phone are not required | D2 |
| FamilyAdmin-provisioned Account | a FamilyAdmin issues an **independent** Account and initial credential inside its own family, and cannot read a member's password or PIN or act as them | D2, D4 |
| Persistent Session | Session survives PWA restart yet supports expiry, refresh, revoke and per-device unlink; revocation withdraws Push authority | D3, D6 |
| Family context separation | `AuthorizedFamilySet` is server-derived from all `ACTIVE` memberships; `ActiveFamilyContext` is foreground convenience and never a security boundary | D1, D3, D7 |
| Scoped RBAC | FamilyAdmin and ServiceAdmin are separate FamilyMembership-scoped roles; default deny; last-admin protection; role changes audited; cross-family denied | D4 |
| Family-scoped route authorization | family-owned routes carry `{familyId}`; the server revalidates Session, membership, owner scope, role/permission and resource ownership instead of trusting the URL | D7 |

## E2 / E3 feature detail

| Feature | Vertical outcome | Frozen basis |
|---|---|---|
| Durable send command | a send persists the message and its Outbox record in **one transaction** before success is reported | D6 |
| Send idempotency | a retry with the same `client_message_id` returns the existing result and creates no second message | D6 |
| Room ordering and cursor | monotonic order per `FamilyGroup + Room`; read cursor advances forward only; **no global ordering** | D6 |
| Transactional Outbox and relay | events are enqueued atomically and drained by a dispatcher; at-least-once with deduplication | D6, D5-C |
| WebSocket gateway | foreground realtime over one logical subscription per `Account + Device + Session`, tolerating multiple concurrent physical sockets | D6 |
| PWA Web Push | background notification bound to Account and device installation, revoked on logout/suspension/Session revoke/device unlink/Account switch | D3, D6 |
| Reconnect / resume / recovery | cursor or resume token replays missed events with deduplication, so Push loss never loses a message | D6 |
| Multi-family subscription | one logical subscription multiplexes the whole `AuthorizedFamilySet`; membership changes update it incrementally; arbitrary client family subscription is denied | D1, D6 |
| Per-family failure isolation | one family's, device's or event's failure never blocks another's delivery | D1, D6 |
| Wagle PIN lock | optional `Account + Device` screen lock; reset not recovery; never readable by FamilyAdmin; never blocks Push, unread counts or other services | D3-PIN-SCOPE |
| Push deep-link authorization | opening a Push revalidates Session, account state, membership, family scope and room/resource permission before showing anything | D6, D7 |

## E4 / E5 feature detail

| Feature | Vertical outcome | Frozen basis |
|---|---|---|
| Owner scope and registration | a service declares `CORE_FAMILY` / `PERSONAL` / `FAMILY` / `PERSONAL_OR_FAMILY`; Registrant, Owner, User, ServiceAdmin and ServicePrincipal stay distinct | D5-A1, D5-A2 |
| Personal service boundary | an Account-owned service stays private across family switch and leave, with no automatic FamilyAdmin access | D5-A1 |
| Activation policy framework | each service declares one of `MEMBER_SELF_ACTIVATE`, `MEMBER_REQUEST_ADMIN_APPROVAL`, `FAMILY_ADMIN_ONLY`, `AUTO_ENABLE_ON_FAMILY_CREATION` | D5-A3 |
| Markpoint access and activation | member request → FamilyAdmin approval, or FamilyAdmin direct activation; `ACTIVE` membership default access that is **not** forced participation; explicit per-member restriction; explicit ServiceAdmin only; registrant never auto-admin; **no `MarkpointParticipant` aggregate** | D5-B |
| Markpoint system actor | automated notifications published as a non-human `ServicePrincipal` 마크포인트 actor into the source family's approved Wagle room, traceable and deduplicated, suppressed while the service is `INACTIVE`/`SUSPENDED` | D5-C |
| Markpoint Target ownership | new Markpoint records are created under `FamilyGroup`/`FamilyMembership` ownership; verified pure business logic is reused; **no legacy row backfill or reconciliation** | D5-B, D8 |
| Markpoint product workflow | mission, approval, point ledger/balance, level/title and reward on Target ownership with server-side authorization | D4, D5-B, D7 |

Wagle is a **Core FamilyGroup capability** (D5-A) and is never gated by a
`ServiceSubscription`; it therefore belongs to E2/E3, never to E4's entitlement
surface.

## E7 feature detail

Every row is `D8 RESET`: validate a fresh start, never migrate. Legacy is
retained read-only, is not a fallback or SSOT, and is destroyed only after the
explicit PM retirement gate.

| Feature | Vertical outcome |
|---|---|
| Fresh target schema validation | the Target schema starts empty with no Player/Admin auto-provisioning |
| Production seed/fixture separation | test, fixture and preview data cannot become Target operational data |
| Empty-state onboarding | a brand-new Account and FamilyGroup can be created and used from empty |
| Opening-ledger invariant | a new Markpoint ledger opens without any legacy balance |
| Legacy write freeze and read-only archive | legacy writes stop and the retained copy is read-only |
| Cutover and post-cutover verification | Target journeys are verified before and after cutover |
| PM-authorized retirement | destructive Legacy deletion happens only after explicit PM approval |

## Evidence and non-goals

The 0a–0g screen source (`MONGLE_NEW_SCREENS_CONTRACT_IMPACT_REVIEW.md`) is UI
**evidence** for E1 and E6, not a decision. Screen-level detail it raises —
discovery privacy, optional additional signup surfaces, membership state-machine
edges — is `DEFERRED_TO_RELEVANT_TASK_START_GATE` for the named UI task and does
not reopen D1–D8.

Explicit non-goals of this decomposition: a generic non-family Group model (D1
rejects it), a `MarkpointParticipant` aggregate (D5-B rejects it), user-facing
`DELIVERED` status (D6 defers it to separate approval), global message ordering
(D6 scopes ordering to `FamilyGroup + Room`), guaranteed Push delivery (D6 makes
Push a notification mechanism only), and any Legacy operational data migration
(D8 rejects it).
