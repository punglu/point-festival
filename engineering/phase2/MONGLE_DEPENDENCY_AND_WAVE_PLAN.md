# Dependency and Wave Plan

> Recalculated against `MONGLE_TARGET_DECISION_FREEZE.md` (D1–D8 `APPROVED` /
> `FROZEN`, 2026-08-01). Waves are derived from real dependencies, not from the
> previous revision's numbering. `D6-P1`–`D6-P8` are
> `DEFERRED_TO_RELEVANT_TASK_START_GATE` and `NON_BLOCKING_FOR_DECOMPOSITION`.

## Task ID versus Wave number

The previous revision used 7 waves (0–6); this one uses 8 (0–7), so the two
numberings no longer align. **Existing task IDs are not renamed** — a `W<n>`
fragment inside an existing ID is a historical identifier only, and the Wave
column in `MONGLE_IMPLEMENTATION_BACKLOG.md` is authoritative for sequencing.
Newly minted IDs use their current wave number.

| Previous wave | Scope then | Current wave |
|---|---|---|
| 0 | decision freeze and contracts | **0** (unchanged, now `DONE`) |
| 1 | identity, session, context, RBAC | **1** (unchanged, plus explicit credential and route-authorization split) |
| 2 | "Wagle durable/realtime" as one wave | split into **2** (durable) and **3** (realtime/Push/recovery/PIN) |
| 3 | Markpoint participant and ownership | **4** (service ownership/activation and Markpoint access) and **5** (Target ownership); the participant aggregate itself is superseded |
| 4 | Markpoint product vertical slices | **5** |
| 5 | UI completion | **6** (with auth/onboarding UI pulled forward as Wave 1 vertical slices) |
| 6 | migration/cutover/operations | **7**, redefined as fresh cutover and Legacy retirement — not migration |

## Critical path

```text
Wave 0 (DONE)
  └─> Wave 1  Account/Credential/Session/Context/RBAC/Route-Authz
        ├─> Wave 2  Wagle durable messaging
        │     └─> Wave 3  Wagle realtime, Push, recovery, PIN
        └─> Wave 4  Service ownership/activation + Markpoint access/system actor
              └─> Wave 5  Markpoint product on Target ownership
                            (system-event relay also needs Wave 3's dispatcher)
  Wave 2/3 and Wave 4/5 run in parallel after Wave 1
        └─> Wave 6  Target UI integration and multi-family journeys
              └─> Wave 7  Fresh cutover and Legacy retirement
```

Wave 1 is the sole serialization point: nothing else can be tested as a real
user journey without an Account-native credential and Session. D8 removes data
migration from the critical path entirely — Wave 7 validates a fresh start
rather than transforming Legacy data.

## Wave 0 — Approved contract freeze and planning closeout

- **Purpose:** freeze D1–D8 and recalculate the plan from them.
- **Preconditions:** PM approval of D1–D8. Met 2026-08-01.
- **Parallel boundary:** documentation only.
- **Start Gate:** PM approval recorded.
- **End Gate:** Decision Freeze reads `APPROVED`/`FROZEN`; contract documents reconciled; `D6-P1`–`P8` registered in `agent-system/active.md`; decomposition/wave/backlog/cutover/DoD documents recalculated.
- **DoD:** no document presents D1–D8 as undecided; the four axes (current implementation, approved contract, deferred policy, legacy reference) are separated.
- **Required tests:** none applicable — no code. Verification is documentary plus `git diff --check`.
- **Entry to next wave:** PM review of this plan and a Wave 1 Start Gate decision.
- **Status:** `DONE`.

## Wave 1 — Account, Credential, Session, Family Context, Scoped RBAC

- **Purpose:** make Account-native login, Session and family-scoped authorization real, replacing the current dependency on legacy PIN/admin login.
- **Preconditions:** Wave 0. Existing `accounts`, `family_groups`, `family_memberships`, `roles`, `permissions`, `role_permissions`, `membership_role_assignments` tables are verified present and reusable.
- **Parallel boundary:** one **security/identity owner** for the credential, Session and authorization dependency. FE auth slices may proceed in parallel only against the frozen backend contract, never by inventing endpoints.
- **Shared-file risk:** the authorization dependency (today's `get_current_user` pair and `resolve_current_account`) and the RBAC seed migration are single-writer. Alembic migration files are single-writer for the whole wave.
- **Start Gate:** confirm the seeded role/permission **code strings** (`REQUIRES_PM_REVIEW`, non-blocking — confirm or rename deliberately, never silently); confirm the credential and Session physical schema design against D2/D3 rather than the historical sketches in `MONGLE_TARGET_COLUMN_DICTIONARY.md`; resolve the suspended authorization defect noted under Risks below.
- **End Gate:** a new Account can be created and can log in with 아이디 + 플랫폼 비밀번호 without any legacy identity; a FamilyAdmin can provision an independent Account inside its own family only; Session survives restart and supports expiry/refresh/revoke/device-unlink; `AuthorizedFamilySet` is server-derived; a family-scoped route rejects a substituted `familyId`.
- **Key DoD:** default deny; server-side revalidation on every family-scoped request; FamilyAdmin cannot read a password or PIN or impersonate; last-admin protection; role changes audited; cross-family access denied.
- **Required tests:** credential login/failure; Session expiry, refresh, revoke and device unlink; FamilyAdmin account-issuance boundaries; multi-membership context; ActiveFamilyContext vs AuthorizedFamilySet separation; FamilyAdmin/ServiceAdmin separation; cross-family deny; arbitrary `familyId` substitution deny.
- **Entry to next wave:** the credential/Session/authorization contract is implemented and its tests actually pass, since Waves 2–5 all authorize against it.

## Wave 2 — Wagle durable messaging foundation

- **Purpose:** make the durable message core satisfy D6 — single-transaction persistence with the Outbox, idempotent send, room-scoped ordering and cursors.
- **Preconditions:** Wave 1. The Doran domain is verified as the durable core candidate (`MONGLE_REALTIME_MESSAGING_CONTRACT.md`).
- **Parallel boundary:** one **messaging durability owner**. Separate from Wave 3's transport owner: Wave 2 owns persistence, ordering and the Outbox write; Wave 3 owns delivery.
- **Shared-file risk:** the message service and its migrations are single-writer. Wave 3 must not modify Wave 2's transaction boundary.
- **Start Gate:** verify whether the existing message persistence and Outbox enqueue already share one transaction; do not assume they do.
- **End Gate:** message and Outbox row commit atomically before `SENT` is reported; a repeated `client_message_id` returns the existing result; order is monotonic per `FamilyGroup + Room`; the read cursor only moves forward; a batch room-list read model exists.
- **Key DoD:** the DB is the SSOT; at-least-once with deduplication; **no global ordering**; no user-facing `DELIVERED`.
- **Required tests:** DB+Outbox atomicity including a forced post-persist failure; idempotent retry; per-room monotonic sequence; cursor recovery; room-scoped visibility.
- **Entry to next wave:** durable history and cursor semantics pass, since recovery in Wave 3 replays from them.

## Wave 3 — Wagle realtime, PWA Push, recovery, PIN

- **Purpose:** deliver messages in the foreground over WebSocket and in the background over Web Push, with DB-based recovery, multi-family multiplexing and the optional PIN lock.
- **Preconditions:** Waves 1 and 2.
- **Parallel boundary:** one **realtime transport owner**. The PIN lock and Push deep-link authorization are separable sub-tasks; presence, mute, bundling, retention and offline-queue work is gated on its own `D6-P` decision.
- **Shared-file risk:** the WebSocket gateway, the Outbox dispatcher and the Push subscription store are three distinct owners; the security dependency they all consume is owned by Wave 1 and consumed read-only here.
- **Start Gate:** obtain the specific `D6-P` decisions a given sub-task needs — `D6-P1` for Push payload, `D6-P2` for mute, `D6-P3` for bundling and foreground suppression, `D6-P4` for read display, `D6-P5` for presence, `D6-P6` for message mutation, `D6-P7` for retention, `D6-P8` for the offline queue. A sub-task whose policy is undecided **must not start**.
- **End Gate:** foreground WebSocket delivery works across multiple physical sockets for one logical subscription; Push arrives in the background and is revoked on logout/suspension/revoke/unlink; a dropped Push is fully recovered from the DB on reconnect with no duplicate display; one logical subscription serves all authorized families; one family's failure does not block another's; a PIN-locked device still receives Push and unread counts without exposing sensitive bodies; a Push deep-link revalidates before showing anything.
- **Key DoD:** Push is never treated as guaranteed delivery or as SSOT; no invariant forbids multiple physical sockets; arbitrary client family subscription is denied.
- **Required tests:** multi-tab and reconnect duplicate suppression; Push subscription and revocation; Push-miss → DB recovery; Push deep-link reauthorization; PIN-locked privacy; one-family failure isolation; incremental subscription update on membership approval and revocation.
- **Entry to next wave:** not a prerequisite for Wave 4, but the dispatcher is required by Wave 5's Markpoint system-event relay.

## Wave 4 — Service ownership/activation and Markpoint access/system actor

- **Purpose:** implement owner scope, registration authority and activation policy, then Markpoint's own access policy and its non-human system actor.
- **Preconditions:** Wave 1 (roles and family-scoped authorization).
- **Parallel boundary:** one **service-ownership owner** for the shared framework; the Markpoint access policy and the system-actor relay are separate sub-tasks. Runs in parallel with Waves 2 and 3 apart from the relay's dispatcher dependency.
- **Shared-file risk:** `ServiceSubscription` and the role/permission tables are shared with Wave 1 — Wave 1 owns them, Wave 4 extends only by additive migration.
- **Start Gate:** each concrete service must name its owner scope and activation policy first; for services other than Wagle and Markpoint that policy is still a PM decision (for example the 가계부 rows) and its task cannot start without one.
- **End Gate:** a FamilyMember can request Markpoint activation and a FamilyAdmin can approve it or activate directly; once `ACTIVE` every `ACTIVE` membership has default access without being forced to participate; an explicit per-member restriction works; ServiceAdmin authority exists only where explicitly assigned; the registrant receives no automatic admin rights; a personal service stays invisible to FamilyAdmin; system notifications post as the `ServicePrincipal` 마크포인트 actor into the source family's approved room only, deduplicated and traceable, and are suppressed while the service is `INACTIVE`/`SUSPENDED`.
- **Key DoD:** Wagle is never subscription-gated; activation is not work authority; **no `MarkpointParticipant` aggregate is created**; `player_id` is never auto-converted to `family_membership_id` or `service_principal_id`.
- **Required tests:** personal vs family owner-scope isolation; FamilyAdmin denied on a personal service; request/approve/reject flows; each activation policy's permitted and denied actor; registrant-not-admin; Markpoint default access and explicit restriction; ServicePrincipal relay authorization, dedup and inactive/suspended deny.
- **Entry to next wave:** Markpoint must be activatable and access-resolvable before its product workflow is built.

## Wave 5 — Markpoint mission, ledger, level and reward on Target ownership

- **Purpose:** build the Markpoint product on `FamilyGroup`/`FamilyMembership` ownership, reusing verified business logic and creating only new records.
- **Preconditions:** Waves 1 and 4; Wave 3's dispatcher for system notifications.
- **Parallel boundary:** one **Markpoint domain owner**. Ordering inside the wave is strict: the Target ownership foundation lands **before** mission/ledger product logic, so product work is never written against legacy `player_id` ownership.
- **Shared-file risk:** the Markpoint domain modules and their migrations are single-writer; the Outbox contract is consumed, not modified.
- **Start Gate:** confirm which pure business logic is being ported and that it is verified by test, not assumed; confirm the target ownership schema; restate explicitly that no legacy row is read for import.
- **End Gate:** a FamilyMembership completes a mission, an authorized ServiceAdmin approves it, and the new ledger and level reflect the result; the new ledger opens with no legacy opening balance; a system notification reaches the family's Wagle room.
- **Key DoD:** server-side authorization on every operation; transactional point/ledger writes; ledger and balance consistency; **no legacy backfill or reconciliation**; test and fixture data separated from operational data.
- **Required tests:** mission lifecycle and approval authority; point ledger and balance transaction integrity; level/title calculation; new-ledger initial invariants; ServiceAdmin-scope authorization and non-admin deny; no legacy or test data contamination.
- **Entry to next wave:** Markpoint's Target journeys pass.

## Wave 6 — Target UI integration and multi-family journeys

- **Purpose:** deliver the real product UI against frozen backend contracts, including genuine multi-family behaviour.
- **Preconditions:** the specific backend contract each slice consumes is implemented and tested. Auth and onboarding UI slices belong to Wave 1's vertical delivery rather than waiting here.
- **Parallel boundary:** one **FE composition owner** per screen family; shared primitives and tokens are single-writer.
- **Shared-file risk:** shared design tokens, the app shell and the `Avatar`-class shared primitives. Note that shared-primitive work is already in flight (see Risks) and must not be duplicated here.
- **Start Gate:** the consumed backend contract is frozen and reachable — no slice may start against static preview fixtures and then claim integration; screen-level deferred items (discovery privacy, additional signup surfaces, membership state-machine edges) must be decided for the slice in question.
- **End Gate:** approved end-to-end Target journeys pass on real APIs, including an account holding three active families receiving another family's message and admin notification while viewing the first.
- **Key DoD:** accessible and responsive; error and empty states real, not decorative; no cross-tab `ActiveFamilyContext` leakage; no invented data where an API field does not exist.
- **Required tests:** target E2E per journey; multi-family concurrent-tab isolation; Push deep-link context switch; accessibility and responsive checks.
- **Entry to next wave:** **Cutover must not begin until Target journey E2E passes.**

## Wave 7 — Fresh cutover and Legacy retirement

- **Purpose:** validate a fresh Target start, freeze and archive Legacy, cut over, verify, and only then retire Legacy under PM approval.
- **Preconditions:** Wave 6 Target journey E2E passes.
- **Parallel boundary:** **single writer for the whole wave.** No parallel product development against the cutover target.
- **Shared-file risk:** deployment, compose, migrations and operational configuration are all single-writer and high-risk.
- **Start Gate:** explicit PM authorization for each destructive or outward-facing step, separately from this plan.
- **End Gate:** the Target schema starts empty with no Player/Admin auto-provisioning; new Account/Family/Markpoint records are created only through Target flows; the ledger opens with no legacy balance; legacy writes are frozen; a read-only Legacy archive exists; post-cutover verification passes.
- **Key DoD:** no Legacy operational data enters Target; Legacy is never an automatic fallback or SSOT; **no destructive Legacy deletion occurs before the explicit PM retirement gate**.
- **Required tests:** `MIGRATION_GUARD` class — empty-schema check, no-Legacy-import check, seed/fixture separation, read-only retention, write-freeze verification, retirement-gate enforcement.
- **Entry to next phase:** PM retirement approval, which is a separate decision this plan does not grant.

## Parallelization rules

1. Two sessions never modify the same file, DB aggregate or API contract concurrently.
2. Wave 1 owns the shared security dependency that Waves 2–5 consume; they consume it read-only and request changes through Wave 1's owner rather than editing it.
3. Wagle durability (Wave 2) and Wagle transport (Wave 3) are separate owners with a fixed boundary at the Outbox: Wave 2 writes it inside the send transaction, Wave 3 reads and dispatches it.
4. Markpoint Target ownership lands before Markpoint product logic — never the reverse.
5. FE work starts only from a vertical slice whose backend contract is frozen and reachable.
6. Cutover (Wave 7) does not start before Target journey E2E passes, and runs single-writer.
7. Alembic migrations, compose, deployment and central configuration are one writer at a time across all waves.

## Deferred policy gates

`D6-P1`–`D6-P8` block only their own Wave 3 sub-tasks and never the wave itself.
Named future-service policies (for example 가계부's activation, access,
visibility, admin and retention rules) block only that service's Wave 4 task.
The register is `agent-system/active.md`.

## Risks carried into Wave 1

These are recorded facts from `agent-system/active.md`, not new findings, and
each should be triaged at the Wave 1 Start Gate rather than discovered mid-wave:

- `PHASE0-AUTOMATED-GAP-CLOSEOUT-001` is `SUSPENDED` with a core defect in **current-user ownership and mutation authorization**. Wave 1 rebuilds exactly that surface, so the defect must be resolved or explicitly scoped into Wave 1 rather than left suspended alongside it.
- `PHASE2-DORAN-MESSAGING-FOUNDATION-001-R2` is `INDEPENDENT_QA_PENDING`, and two Doran commits (`0393971`, `91eb98e`) extended the domain with no task record. Wave 2 depends on that domain, so its actual state must be verified rather than taken from the stale handoff.
- `MONGLE-W6-1-AVATAR-STATUS-DOT-CLIP-FIX-001` is a shared-primitive change pending independent QA, and A1 visual work sits in a separate worktree pending a PM visual gate. Wave 6 must not duplicate or bypass either.
