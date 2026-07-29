# Doran Secure Messaging Contract R2

**Status:** APPROVED CONTRACT / canonical R2 (2026-07-26)
**Authority:** this document supersedes conflicting Phase 2 target notes. It is
a design contract, not proof of implementation, QA PASS, commit, or push.

## Status vocabulary and current state

`APPROVED CONTRACT` is required behavior; `IMPLEMENTED` needs execution
evidence; `DEFERRED` is intentionally not delivered; `QA FAILED` is known not
to satisfy the contract. The isolated Foundation is
`PARTIALLY_IMPLEMENTED / QA_FAILED / UNCOMMITTED / UNPUSHED`; it is not this
contract's authority.

Mongle is the Platform, Doran is its Family-scoped messaging service. Canonical
names are `doran.*` permissions, `doran_*` tables, and Room role `room_admin`.
Historical `messaging.*`, `conversation_*`, and Room `owner` names are migration
notes only and must not be used by new code or registry entries.

## Authority planes and actors

| Plane | Authority | Explicit non-authority |
| --- | --- | --- |
| Platform control | platform configuration/operators | universal Room-content bypass |
| Family governance | Membership, Family roles, subscription installation | Room participation or Room admin |
| Doran Room | Room/Participant/Message/read state | Family governance or service control |
| Attached service | subscription, Service Principal, binding/action | Doran Room admin or user identity |

`services.manage ≠ service-internal admin ≠ doran.rooms.manage ≠ message
publish`. Family `owner`/`admin` do not read a non-participant Room. Platform
Operator is separate from User Account and has no content access absent a later,
audited break-glass policy.

Actors are: (1) **User Account**, authenticated by user JWT and resolved to an
active Membership; server derives sender, never the request; (2) **Service
Principal**, not a User Account and never a user JWT/impersonation, constrained
by Family/service audience and Service–Room Binding; and (3) **Platform
Operator**, with no automatic Family/Room/Service grant.

## Room and participation contract

Every v1 Room is Family-scoped: `DIRECT`, `GROUP`, or `SERVICE`.

- DIRECT has exactly two distinct active Memberships in one Family. The ordered
  membership pair is canonical; one active pair exists per Family even under
  concurrent creation. Archive hides that canonical Room from a user's list;
  a renewed conversation reopens the same Room and preserves history. Reopen is
  denied when either counterparty has left or been removed from the Family.
- GROUP has explicit Participants. `room_admin` manages only its Room; Family
  governance roles do not auto-participate.
- SERVICE is tied to an active/past Family subscription and permits publication
  only by an allow-listed Service Principal through an explicit binding.

Participant states are `ACTIVE`, `LEFT`, and `REMOVED`. A joining Participant
sees sequences `>= joined_sequence`; a voluntary leaver reads only through
`left_sequence`; a removed Participant immediately loses every Room/message/read
API. Rejoin creates a new participation period. Current Account, Membership,
Family, subscription, and Participant eligibility is rechecked on each request.

## Message, ordering, deletion, and read state

Message types are `TEXT`, `SYSTEM`, and `SERVICE_ACTION`.

- Room-local server-assigned monotonic `sequence` is canonical; `(room_id,
  sequence)` is unique. Cursor order is `(sequence, message_id)`; timestamp is
  never the order authority. Gaplessness is not promised.
- TEXT is User Account-authored; editing is absent in v1. Its sender may soft
  delete it, preserving metadata/sequence and returning a body-free tombstone.
- SYSTEM is server-authored and immutable to users.
- SERVICE_ACTION is Service Principal-authored through Binding and a versioned
  allow-listed schema. Doran stores only a display-minimum snapshot and owning
  service reference; the owning service is SSOT for business state and detailed
  events. Action execution reauthorizes against that service's current state.
  URLs, commands, arbitrary payloads, and user-issued service identities are
  denied.
- Participant read state is a monotonic visible sequence. Own sends are excluded
  from unread counts unless a later approved policy says otherwise.

## Idempotency, transaction, and subscription

User message idempotency scope is
`sender_participant_id + room_id + client_message_id`.

| Retry | Required result |
| --- | --- |
| same ID, same canonical payload | same logical message; never HTTP 500, including concurrency |
| same ID, different payload | HTTP 409; no mutation |

Sequence allocation and Message insert occur in one top-level UoW. Router and
helpers do not commit. Concurrent sequence conflicts cannot leak as HTTP 500.
Suspended/cancelled subscription preserves eligible Participant history and read
state only; it blocks Room creation, send, participant/Room mutation, delete,
and Service Action. Inactive Account/Family/Membership or removed Participant
always wins over read-only retention.

Service-event idempotency includes `source_event_id` within the authenticated
Service Principal/source scope. Service business writes and
message/event publication require a Transactional Outbox; Doran DB direct
inserts by services are forbidden. Outbox is **DEFERRED / NOT IMPLEMENTED**.

## Family-scoped HTTP contract

All resources live below `/api/families/{family_id}/doran`. Requests allowlist
client fields and reject/ignore client control of `family_id`, sender Account or
Participant, sequence, Service Principal, system type, timestamps, and delete
metadata. API evaluation is: authenticate Account → active Membership/Family →
required `doran.*` permission → resource Family → Participant/Room rule →
subscription rule → UoW.

Lists are cursor based: initial recent page, `before_sequence` history, and
`after_sequence` reconnect sync are mutually exclusive. Responses hide deleted
bodies and inaccessible Participation history. R2-A defaults are TEXT body at
most 4,000 characters, page default 50/max 100, GROUP Participants at most 50,
and `client_message_id` at most 64 characters. Send/create rate, event-payload,
WebSocket frame, and connection limits remain R2-B/Realtime measurement work;
they must not default to unbounded when those APIs are delivered.

## Security, privacy, realtime, and migration

Audit (without plaintext message body, full sensitive action payload, token, or
credential) covers Room/Participant/room_admin/Binding changes, Service
publication failure, denial, and future break-glass. Retention, erasure,
report/block, legal hold, and break-glass are **DEFERRED**. No operator content
access exists before a separately approved policy; neither legal hold nor E2EE
is claimed.

WebSocket is an auxiliary delivery path, never source of truth: short ticket,
Origin allowlist, connection/auth recheck, revoke, cursor sync, duplicate
defence, batching/backpressure, and limits are required. It is **NOT
IMPLEMENTED / DEFERRED**.

Future migrations must exercise upgrade/downgrade/re-upgrade in real PostgreSQL,
remove R2 registry data on downgrade or explicitly fail with assigned data, and
pass catalog checks under a separate operating-data Human Gate.

## Delivery phases

| Phase | Scope | Current state |
| --- | --- | --- |
| R2-A Foundation | DB, Rooms, Participants, Messages, Read State, HTTP, sequence, user idempotency, tombstone, tests | PARTIAL / QA FAILED |
| R2-B secure service | Platform boundary, Principal, Binding, event idempotency, Outbox, audit, limits, Dock backend | NOT IMPLEMENTED |
| Realtime | ticket, revoke, sync, backpressure, limits | DEFERRED |
| Frontend UX | Room UX, virtualized timeline, media, reconnect, Dock UX | DEFERRED |
| Mark Point pilot | Principal, Binding, action schema/revalidation | DEFERRED |

R2-A repair is authorized only for namespace/schema alignment, idempotency and
downgrade repair, and deterministic PostgreSQL integration/concurrency tests.
Service Principal, Outbox, Dock, Realtime, and UI remain outside R2-A.
