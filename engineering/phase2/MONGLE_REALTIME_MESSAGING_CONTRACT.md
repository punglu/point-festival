# MONGLE_REALTIME_MESSAGING_CONTRACT

Task: MONGLE-DATA-BACKEND-CONTRACT-RECONCILIATION-001 (Axis B)

> **STATUS: PARTIALLY_SUPERSEDED_BY_MONGLE_TARGET_DECISION_FREEZE.** Current-code evidence below remains valid as `CURRENT IMPLEMENTATION`. The `APPROVED TARGET CONTRACT` is D6 (with D1/D3/D5-A/D5-C/D7) in `MONGLE_TARGET_DECISION_FREEZE.md`, restated in §"Approved D6 Target contract" below.

와글와글 (Wagle) is a **Core FamilyGroup capability** per approved D5-A — never gated by `ServiceSubscription`. The already-implemented Doran domain is the **durable messaging core candidate** for Wagle's Target contract: its Room/Participant/Message/ReadState/ServicePrincipal shape and its idempotency and ordering guarantees are strong, evidence-backed matches. It is **not** a completed Wagle realtime target — the D6 realtime transport, Web Push and recovery layer does not exist in code. Do not read the sections below as "Wagle is done".

## Approved D6 Target contract (`APPROVED`, 2026-08-01 — implementation not built)

This is binding design, not a completion claim. Full text in the Decision Freeze.

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

## Current implementation evidence (Doran domain, durable core candidate)

Everything in this section is verified current code, retained as reuse-fitness evidence for the D6 durable-messaging layer. `KEEP_AS_IS` here means "no change identified by this inventory", not "satisfies D6".

- **Identity model**: every actor is either a Membership (a human, scoped to one Group) or a Service Principal (a non-human, credentialed actor belonging to no Group directly, but Bound to specific Group+Room pairs). Never a legacy Player. Evidence: `doran/models.py`, `doran/service_actor.py`.
- **Room types**: `DIRECT` (canonical 1:1 pair per two Memberships in a Group, enforced by a partial unique index so re-opening after close doesn't collide), `GROUP` (multi-Membership, max 50 active participants, enforced), `SERVICE` (one canonical broadcast Room per Group per Attached Service, created only as a side effect of a Service Binding). Evidence: `doran/models.py:11-43`, `doran/service.py:57-93,201`.
- **Message ordering**: a per-Room monotonic `sequence` counter, atomically incremented via `UPDATE ... RETURNING`, giving gapless, race-safe ordering without relying on wall-clock timestamps for ordering (`created_at` exists but is not the ordering key). Evidence: `doran/service.py:128,482`.
- **Idempotency**: human sends are deduplicated by `(sender_participant_id, room_id, client_message_id)`; Service Principal publishes are deduplicated by `(service_principal_id, source, source_event_id)` — both via a real unique DB constraint plus an `IntegrityError`-catch-and-reselect pattern, not just an application-level check-then-write. Evidence: `doran/models.py:108-109`, migration `0003...`:55-61, `doran/service.py:123-139,467-509`.
- **Deletion**: tombstone pattern — a deleted message keeps its row (`deleted_at`+`deleted_by_account_id` set) and the API still returns it with `deleted: true`, never a hard delete. Evidence: `doran/schemas.py:88-90`.
- **Read tracking**: one watermark (`last_read_sequence`) per Participant, not a per-message read-by list; unread count is computed on demand by comparing the watermark against the Room's visible sequence range. Evidence: `doran/models.py:124-129`, `doran/service.py:154-190`.
- **Visibility window**: a Participant only ever sees messages between their own `joined_sequence` and (if they've left) `left_sequence` — joining late does not retroactively reveal a GROUP room's prior history, but a SERVICE room broadcasts from sequence 0 regardless of when a Membership onboards, since it's a Group-wide log, not a private conversation. Evidence: `doran/rules.py:11-14`, `doran/service.py:392-399` (comment explicitly contrasts the two cases).
- **Cross-service publishing (MarkPoint -> 와글와글)**: a Service Principal, authenticated by its own Bearer-credential scheme (never a user JWT), may publish only pre-registered `(action_type, schema_version)` pairs into exactly the Rooms it holds an active Binding for, with a bounded (2000-byte) "display-minimum" snapshot payload — never the business decision itself, never free-form. Evidence: `doran/service_actor.py`, `doran/schemas.py:126-144`, `doran/service.py:428-509`.
- **Authorization**: every operation resolves the caller's Account -> active Membership -> effective Permissions (Role-derived, Service-Subscription-gated for SERVICE-scope permissions) before touching any Room; a suspended/cancelled Doran subscription still preserves read access (`doran.messages.read` is deliberately retained even when the subscription lapses — a documented, intentional exception, not a bug) but blocks every write. Evidence: `doran/service.py:46-54,113`.

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

**Physical naming** — whether `doran_*` tables and the `doran` service_code should be renamed to a `wagle`-prefixed convention matching the product's Korean name is cosmetic and remains `REQUIRES_PM_REVIEW`. D1–D8 do not decide it, it blocks no decomposition, and it must not be resolved as a side effect of another task. Logical/product name: 와글와글 (Wagle). Current physical name: `doran`.
