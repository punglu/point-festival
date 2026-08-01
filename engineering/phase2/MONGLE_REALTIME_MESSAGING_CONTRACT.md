# MONGLE_REALTIME_MESSAGING_CONTRACT

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

> **STATUS: PARTIALLY_SUPERSEDED_BY_MONGLE_TARGET_DECISION_FREEZE.** Current-code evidence below remains valid as `CURRENT IMPLEMENTATION`. The `APPROVED TARGET CONTRACT` is D6 (with D1/D3/D5-A/D5-C/D7) in `MONGLE_TARGET_DECISION_FREEZE.md`, restated in §"Approved D6 Target contract" below.

와글와글 (Wagle) is a **Core FamilyGroup capability** per approved D5-A — never gated by `ServiceSubscription`. The already-implemented Wagle domain (historically named Doran) is the **durable messaging core candidate** for Wagle's Target contract: its Room/Participant/Message/ReadState/ServicePrincipal shape and its idempotency and ordering guarantees are strong, evidence-backed matches. It is **not** a completed Wagle realtime target — the D6 realtime transport, Web Push and recovery layer does not exist in code. Do not read the sections below as "Wagle is done".

## Wave 2 durable slice — implemented 2026-08-01

`MONGLE-W2-WAGLE-DURABLE-MESSAGING-AUTONOMOUS-001` implemented the **durable**
half of the D6 contract. What changed, and what deliberately did not:

| D6 element | State after Wave 2 |
|---|---|
| Atomicity (message + Outbox in one Transaction) | **IMPLEMENTED.** `send_message` appends a `service_outbox_events` row (`owner_service="wagle"`, `event_type="wagle.message.created"`, `aggregate_type="wagle_message"`, v1) inside the same transaction as the message insert and the room-sequence advance. A forced post-persist failure is proven by test to roll back all three. Before this Wave the send path wrote **no** Outbox row at all — the atomicity requirement was unmet rather than partially met. |
| DB as SSOT for message/ordering/read | **IMPLEMENTED** (pre-existing, now pinned by test). |
| Per-`FamilyGroup + Room` ordering, no global order | **IMPLEMENTED** (pre-existing). Two rooms are proven to hold independent sequence spaces. |
| `client_message_id` deduplication | **IMPLEMENTED** (pre-existing). Same id + different body is a 409. |
| Batch room list with preview and unread | **IMPLEMENTED.** New `GET /room-summaries`. |
| Foreground WebSocket transport | **NOT IMPLEMENTED** — Wave 3. |
| Web Push, subscription, revocation | **NOT IMPLEMENTED** — Wave 3. |
| Outbox **consumption** / dispatcher | **NOT IMPLEMENTED** — Wave 3. Wave 2 only records the event durably. |
| Reconnect cursor / resume | **NOT IMPLEMENTED** — Wave 3. The stored `(room_id, sequence)` shape does not obstruct it. |
| Presence, mute, bundling, read display, retention, offline queue | **NOT IMPLEMENTED** — each gated on its own `D6-P` decision. |

The event envelope Wave 3 can rely on: `id`, `event_type`, `event_version`,
`aggregate_type`/`aggregate_id`, `source_event_id` (the message UUID, which is
what makes the enqueue idempotent), `family_id`, `payload`
(`family_group_id`, `room_id`, `message_id`, `sequence`, `message_type`,
`sender_participant_id`, `occurred_at`), plus the existing delivery-state
columns `status`, `attempt_count`, `next_attempt_at`, `locked_until`,
`published_at`, `last_error_code`.

### Naming contract (corrected 2026-08-01 by PM decision)

**Wagle is the Target name. Everything this domain newly emits uses it.**
`wagle` survives only as a historical implementation name — module path, table
names, route prefix, and the seeded permission/subscription codes that already
exist in data.

| Emitted by Wave 2 | Value |
|---|---|
| Outbox `owner_service` | `wagle` |
| Outbox `event_type` | `wagle.message.created` |
| Outbox `aggregate_type` | `wagle_message` |

An earlier revision of Wave 2 emitted the historical name for all three, on the
reasoning that reusing the registered service code avoids a second identifier
for one service. **That was wrong and was retracted by PM decision.** The naming
split the Data Naming Contract warns about is uncontrolled renaming of
*existing* data; it is not a licence for new Target contracts to inherit the
legacy name.

**The whole runtime is now Wagle** — completed 2026-08-01 by migration `0007`
under `MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001`, which moved every
active identifier in one atomic step:

| Identifier | Now |
|---|---|
| Service code | `wagle` (roles, `service_subscriptions`, `service_principals`) |
| Permission codes | `wagle.messages.read/send`, `wagle.rooms.create/manage`, `wagle.participants.manage` |
| Route prefix / OpenAPI tag | `/api/families/{familyId}/wagle/...`, tag `wagle` |
| Tables, indexes, constraints, trigger functions | `wagle_*` |
| Python module | `app.domains.wagle` |

Renaming the permission *codes* in place preserved every `role_permissions`
binding, because those rows reference `permissions.id`, not the code string. The
trigger functions were dropped and recreated rather than renamed: PostgreSQL
stores a plpgsql body as text, so a function selecting `FROM doran_rooms` would
have kept doing so after the table moved and failed at call time.

**No compatibility layer was kept.** The historical route prefix is not served
and returns 404; there is no permission fallback, no service-code fallback, no
dual seed and no translation map. The historical name survives only as the
rename's source value inside migration `0007`, in Axis-A/historical documents,
and in past commit messages.

## Approved D6 Target contract (`APPROVED`, 2026-08-01 — implementation not built)

This is binding design, not a completion claim. Full text in the Decision Freeze.
Superseded in part by the Wave 2 table above: the atomicity, ordering,
deduplication and DB-SSOT rows are now built. Transport, Push, recovery and
every `D6-P` policy row remain unbuilt.

| Element | Approved contract |
|---|---|
| Foreground realtime | WebSocket |
| Background notification | PWA Web Push |
| SSOT for message, ordering, read state | the server's durable DB — never WebSocket or Push |
| Atomicity | message persistence and its Outbox record commit in **one Transaction boundary**; success is reported to the sender only after that commit |
| Delivery semantics | `at-least-once`. `exactly-once` is not claimed and must not be implemented as if guaranteed |
| Deduplication | unique `message_id`/`event_id` server-side, `client_message_id` sender-side; both client and server deduplicate |
| Ordering | per `FamilyGroup + Room` only, via `room_sequence` or equivalent monotonic counter. **Global ordering is not required and must not be built** |
| User-visible send states | `PENDING`, `SENT`, `FAILED`, `READ`. A user-facing `DELIVERED` state must not be introduced without separate PM approval |
| Subscription scope | `Account + Device + Session` is **one logical** subscription. Multiple physical WebSockets may legitimately coexist across tabs, reconnects and connection replacement — each needs its own connection ID and server lifecycle/dedup. **Do not write an invariant forbidding multiple physical sockets** |
| Family multiplexing | one logical subscription serves the entire `AuthorizedFamilySet`. `ActiveFamilyContext` never suppresses another authorized family's realtime or Push |
| Membership revocation | revoking one FamilyMembership ends only that family's subscription; other families continue |
| Push status | a notification mechanism only — never guaranteed delivery and never the SSOT |
| Recovery | Push loss, delay or duplication is recovered from the durable DB via Cursor/Resume Token, not by trusting Push |
| Push open | revalidates Session, Account state, FamilyMembership, family scope and Room/Resource permission before showing anything |
| PIN interaction | a locked Wagle PIN preserves Push and unread counts while minimising sensitive body content; it never blocks background Push or other services |
| Failure isolation | one family's, device's or event's failure never blocks another family, device or event. Outbox, cursor, read state, unread count and retry/failure records are isolated per FamilyGroup |

### Deferred D6 policies

`D6-P1`–`D6-P8` are `DEFERRED_TO_RELEVANT_TASK_START_GATE` and
`NON_BLOCKING_FOR_DECOMPOSITION`. No default is assumed. A task whose scope
depends on one of them must not be promoted to `READY_FOR_IMPLEMENTATION` until
PM decides it. Register: `agent-system/active.md`.

## Current implementation evidence (Wagle domain, durable core candidate)

Everything in this section is verified current code, retained as reuse-fitness evidence for the D6 durable-messaging layer. `KEEP_AS_IS` here means "no change identified by this inventory", not "satisfies D6".

- **Identity model**: every actor is either a Membership (a human, scoped to one Group) or a Service Principal (a non-human, credentialed actor belonging to no Group directly, but Bound to specific Group+Room pairs). Never a legacy Player. Evidence: `wagle/models.py`, `wagle/service_actor.py`.
- **Room types**: `DIRECT` (canonical 1:1 pair per two Memberships in a Group, enforced by a partial unique index so re-opening after close doesn't collide), `GROUP` (multi-Membership, max 50 active participants, enforced), `SERVICE` (one canonical broadcast Room per Group per Attached Service, created only as a side effect of a Service Binding). Evidence: `wagle/models.py:11-43`, `wagle/service.py:57-93,201`.
- **Message ordering**: a per-Room monotonic `sequence` counter, atomically incremented via `UPDATE ... RETURNING`, giving gapless, race-safe ordering without relying on wall-clock timestamps for ordering (`created_at` exists but is not the ordering key). Evidence: `wagle/service.py:128,482`.
- **Idempotency**: human sends are deduplicated by `(sender_participant_id, room_id, client_message_id)`; Service Principal publishes are deduplicated by `(service_principal_id, source, source_event_id)` — both via a real unique DB constraint plus an `IntegrityError`-catch-and-reselect pattern, not just an application-level check-then-write. Evidence: `wagle/models.py:108-109`, migration `0003...`:55-61, `wagle/service.py:123-139,467-509`.
- **Deletion**: tombstone pattern — a deleted message keeps its row (`deleted_at`+`deleted_by_account_id` set) and the API still returns it with `deleted: true`, never a hard delete. Evidence: `wagle/schemas.py:88-90`.
- **Read tracking**: one watermark (`last_read_sequence`) per Participant, not a per-message read-by list; unread count is computed on demand by comparing the watermark against the Room's visible sequence range. Evidence: `wagle/models.py:124-129`, `wagle/service.py:154-190`.
- **Visibility window**: a Participant only ever sees messages between their own `joined_sequence` and (if they've left) `left_sequence` — joining late does not retroactively reveal a GROUP room's prior history, but a SERVICE room broadcasts from sequence 0 regardless of when a Membership onboards, since it's a Group-wide log, not a private conversation. Evidence: `wagle/rules.py:11-14`, `wagle/service.py:392-399` (comment explicitly contrasts the two cases).
- **Cross-service publishing (MarkPoint -> 와글와글)**: a Service Principal, authenticated by its own Bearer-credential scheme (never a user JWT), may publish only pre-registered `(action_type, schema_version)` pairs into exactly the Rooms it holds an active Binding for, with a bounded (2000-byte) "display-minimum" snapshot payload — never the business decision itself, never free-form. Evidence: `wagle/service_actor.py`, `wagle/schemas.py:126-144`, `wagle/service.py:428-509`.
- **Authorization**: every operation resolves the caller's Account -> active Membership -> effective Permissions (Role-derived, Service-Subscription-gated for SERVICE-scope permissions) before touching any Room; a suspended/cancelled Wagle subscription still preserves read access (`wagle.messages.read` is deliberately retained even when the subscription lapses — a documented, intentional exception, not a bug) but blocks every write. Evidence: `wagle/service.py:46-54,113`.

## Gap between current implementation and the approved D6 contract

These are **implementation gaps**, not open product decisions. D6 already decides the contract; each row is scoped to a Wave 2/Wave 3 task.

1. **WebSocket foreground transport** — every current route is plain HTTP request/response (poll-based read, explicit send). No WebSocket or SSE delivery exists. D6 **approves WebSocket and rejects a polling-only Target**, so this is `IMPLEMENTATION_REQUIRED`, no longer `UNDECIDED`.
2. **PWA Web Push** — no push subscription, dispatch, revocation or deep-link authorization mechanism exists. Approved by D6; `IMPLEMENTATION_REQUIRED`.
3. **Outbox relay worker** — `service_outbox_events` rows are enqueued by Markpoint on mission completion, but nothing drains them into `publish_service_action`. No worker/consumer exists in `backend/app`. Required for D5-C system notifications and D6 dispatch.
4. **Reconnect / resume / recovery** — no Cursor or Resume Token protocol exists for replaying missed events after reconnect, restart, device sleep or Push loss. Approved by D6; `IMPLEMENTATION_REQUIRED`.
5. **Multi-family logical subscription** — no code multiplexes an `AuthorizedFamilySet` over one logical subscription, and no incremental subscription update on membership approval/revocation exists. Approved by D1/D6; `IMPLEMENTATION_REQUIRED`.
6. **Transactional atomicity verification** — current message persistence and Outbox enqueue need verification against D6's single-Transaction requirement before reuse is accepted.
7. **Wagle PIN local lock** — no `Account + Device` screen lock exists. Approved by D3-PIN-SCOPE; `IMPLEMENTATION_REQUIRED`.
8. **Batch room-list read model** — no endpoint returns "rooms + last message preview + unread count" in one call; `list_rooms` returns bare Room rows. A real room-list screen needs this; the response shape is design work for its own task.
9. **Frontend wiring** — `DoranLanding.tsx` and its component tree render exclusively from static preview fixtures; none of the backend contract is reachable from the live UI.

## Still-open naming question (not a D1–D8 decision, blocks nothing)

**Physical naming** — whether `wagle_*` tables and the `wagle` service_code should be renamed to a `wagle`-prefixed convention matching the product's Korean name is cosmetic and remains `REQUIRES_PM_REVIEW`. D1–D8 do not decide it, it blocks no decomposition, and it must not be resolved as a side effect of another task. Logical/product name: 와글와글 (Wagle). Current physical name: `wagle`.
