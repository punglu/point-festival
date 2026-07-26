# Doran Security and Authorization R2

**Status:** APPROVED CONTRACT / canonical R2 (2026-07-26)
**Authority:** complements [DORAN_MESSAGING_CONTRACT.md](DORAN_MESSAGING_CONTRACT.md). It specifies required behavior, not implemented behavior.

## Authority separation

| Plane | May decide | Must not imply |
| --- | --- | --- |
| Platform control | platform operations and configuration | Family, Room, or Service access; ordinary message-content access |
| Family governance | Membership, Family role, service installation/subscription | Room participation, `room_admin`, or non-participant Room read |
| Doran Room | Room lifecycle, Participants, messages, read state | service administration or user impersonation |
| Attached Service | service administration, Principal, Binding, service Action policy | Family governance, `room_admin`, or a user identity |

There is no universal data bypass. A future operator break-glass process is a
separate, audited policy and is **DEFERRED**. Family `owner` and `admin` are
Family governance roles; `room_admin` is the only Room-management role.

## Actors and credential boundaries

| Actor | Authentication | Allowed identity | Prohibited identity behavior |
| --- | --- | --- | --- |
| User Account | user JWT | current authenticated Account and active Family Membership | client-selected sender Account/Participant, sequence, or service identity |
| Service Principal | service-specific credential | one service, Family audience, and explicit Service–Room Binding | user JWT reuse, user impersonation, direct database insert |
| Platform Operator | platform operational authentication | narrowly granted control action | automatic Room-body read or general Family/Room bypass |

The server resolves the User Account's active Membership and active Participant.
It never accepts a user request's sender identity as authority. A Service
Principal is visibly service-authored and can emit only the allow-listed schema
in an allowed Binding.

## Required Doran permissions

New registry entries use `doran.*` only.

| Permission | Scope of grant | Additional rule |
| --- | --- | --- |
| `doran.rooms.create` | eligible active Family Membership | active subscription; DIRECT target and Room policy must also pass |
| `doran.rooms.manage` | `room_admin` or separately authorized Room manager | no automatic message-body access without participation |
| `doran.participants.manage` | `room_admin`/authorized Room manager | target must be an eligible Membership in the same Family |
| `doran.messages.read` | active or permitted LEFT Participant | visibility period is still mandatory |
| `doran.messages.send` | active Participant | active subscription and TEXT-only user API |

Deletion is not a Family-admin moderation power: only the active author of a
TEXT message may request its tombstone. A standalone moderation permission,
report/block, retention, and legal-hold policy are **DEFERRED**.

## Authorization evaluation

Every API and reconnect request evaluates the following in order:

1. authenticate the actor;
2. resolve active Account, Family, and Membership eligibility;
3. validate URL Family/resource Family equality;
4. evaluate the required `doran.*` permission;
5. resolve current Participant state and the applicable participation period;
6. apply Room type and requested-operation rules;
7. apply subscription state; and
8. apply payload allowlist and execute in the top-level UoW.

An inactive/suspended/deleted Account, inactive/closed Family, inactive/left/
removed Membership, Family mismatch, or removed Participant denies access before
subscription read-only retention. A cursor is not a capability: its Room and
the caller's current authorization are revalidated every request.

## Subscription boundary

For suspended or cancelled Doran subscription, an otherwise eligible existing
Participant may read visible history and advance a visible read state. Room
creation, send, Room/Participant mutation, message delete, and Service Action
are denied. Service subscription does not grant any User Account a Room role;
Family service installation does not grant Service Principal publication.

## HTTP object and error boundary

The request model is allowlisted. Clients cannot set `family_id`, sender Account
or Participant, `sequence`, Service Principal, `SYSTEM`/`SERVICE_ACTION` type,
timestamps, deletion fields, or authorization fields. Cross-Family object
substitution, non-participant reads/writes, and removed-participant access must
fail without mutation. Same idempotency key plus changed canonical payload is
HTTP 409; a retry of the same payload must return the existing logical message,
including under concurrent requests.

Responses omit tombstoned message body and inaccessible history. Error detail
must not leak another Family's Room existence, participant data, credential, or
plaintext message body.

## Family-scoped endpoint matrix

All endpoints are below `/api/families/{family_id}/doran`; each uses the common
authorization order above. `R` means eligible visible history/read-state is
allowed while subscription is suspended/cancelled; `A` means active subscription
is required.

| Endpoint | Permission and participant rule | Subscription | Allowlisted request / response visibility | Cursor/idempotency | Error / mutation |
| --- | --- | --- | --- | --- | --- |
| `GET /rooms` | active Membership; return only Rooms with a current eligible participation period | R | no caller-controlled Family; list excludes inaccessible/deleted Rooms | bounded Room-list pagination if supplied | deny/empty policy must not enumerate inaccessible Rooms; no mutation |
| `POST /rooms` | `doran.rooms.create`; server resolves creator/current Membership | A | type, title, DIRECT target Memberships or GROUP initial eligible Participants only | DIRECT canonical create is race-safe; request idempotency policy must be explicit before API delivery | validation/authorization failure has no mutation; creates Room + initial Participants atomically |
| `GET /rooms/{room_id}` | `doran.messages.read` plus visible Participant period | R | no hidden Room metadata/body exposure | none | deny without mutation |
| `PATCH /rooms/{room_id}` | `doran.rooms.manage` and `room_admin` rule | A | allowlisted mutable Room metadata only | optional operation key must be defined if retries are offered | deny/no mutation or one Room UoW mutation |
| `GET /participants` | current eligible Room Participant; management-only fields restricted to `room_admin` | R | response omits inaccessible historical identity detail | bounded pagination if needed | deny/no mutation |
| `POST /participants` | `doran.participants.manage` and `room_admin`; GROUP only unless later contract says otherwise | A | target Membership only; same Family and active eligibility required | duplicate/rejoin lifecycle explicit, not client-selected status/sequence | deny/no mutation or Participant UoW mutation |
| `DELETE /participants/{participant_id}` | `doran.participants.manage` and `room_admin`; cannot bypass DIRECT lifecycle policy | A | no client-selected removal actor/sequence | operation retry is idempotent by resulting lifecycle state | deny/no mutation or removal UoW mutation |
| `POST /leave` | caller's active Participant; not a general DIRECT leave API | A | no caller-selected Participant/leave sequence | resulting LEFT state is retry-safe | deny/no mutation or leave UoW mutation |
| `GET /messages` | `doran.messages.read` and current/LEFT visible range | R | response hides pre-join/post-left and tombstone bodies | `before_sequence` xor `after_sequence`; bounded limit | malformed/foreign cursor fails safely; no mutation |
| `POST /messages` | `doran.messages.send` and active Participant | A | user API allows TEXT body plus `client_message_id` only | scoped message idempotency is mandatory | same payload returns existing; changed payload 409; Room counter + Message one UoW |
| `DELETE /messages/{message_id}` | active TEXT author only, plus current active Participant | A | no deletion actor/time/type from client; response is tombstone | repeated delete is idempotent | SYSTEM/SERVICE_ACTION/other author denied; tombstone UoW only |
| `GET /read-state` | own current or LEFT visible Participant period | R | returns own state and derived unread only | none | deny/no mutation |
| `PUT /read-state` | own non-removed Participant, visible sequence only | R | `last_read_sequence` only | monotonic max update; equal/lower is safe no-op | out-of-range/foreign state denied; one read-state UoW mutation |

`SERVICE_ACTION` and Service Principal endpoints are not exposed by the user
HTTP API until R2-B Binding, schema, outbox, and authorization are delivered.

## Service Actions and outbox

`SERVICE_ACTION` is an event envelope, not a privileged command channel. It
uses a versioned allowlist schema and `source_event_id` replay defence. Doran
stores only a display-minimum snapshot and owning-service reference; the owning
service revalidates its authorization/current business state and remains SSOT
for detailed events. URLs, arbitrary commands, free-form executable payloads,
and unregistered schemas are denied. Service business mutation and associated
Doran publication require a Transactional Outbox with idempotent consumption.

Service Principal, Binding, event idempotency, outbox, and service Action APIs
are **NOT IMPLEMENTED / DEFERRED TO FOUNDATION R2-B**.

## Audit and privacy

Audit records cover Room create/archive, Participant and `room_admin` mutation,
Binding mutation, service-publication failure, permission denial, and every
future break-glass access. Default audit content excludes plaintext message
bodies, full sensitive Action payloads, tokens, and service credentials.

Message retention, erasure, reporting, blocking, legal preservation, and
break-glass approval/escalation are **DEFERRED**. No operator message-content
access exists before separate PM approval. Doran makes neither legal-hold nor
E2EE claims.
