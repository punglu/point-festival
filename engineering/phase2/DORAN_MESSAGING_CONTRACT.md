# Doran Messaging Contract

**Status:** TARGET CONTRACT / PM_REVIEW_REQUIRED (2026-07-26)
**Scope:** design only; no current schema, API, WebSocket, or UI is created.

## Current and target boundary

The legacy chat is a **LEGACY REFERENCE**: one `chat_messages` row holds
`sender_id`, `receiver_id`, text, per-message `is_read`, and a server timestamp.
It is player-based, 1:1-only, polls every 15 seconds in the frontend, and has no
Room, Account, Family, Membership, participant, event, or device contract.

Doran is Naran's family-scoped conversation service. Mark Point may create an
event or Action Message, but Doran never becomes the authority for mission or
point state.

## Domain lifecycle

```text
active Account + active Family Membership + active Doran subscription
→ active Room Participant + required Permission
→ read/send/manage the Room
```

Every v1 user conversation belongs to one Family Group. Platform-private
notifications remain the Notification domain; no personal cross-family room is
introduced in v1.

## Room types

| Type | Target use | Rule |
| --- | --- | --- |
| `DIRECT` | two active Family members | exactly two active participants; duplicate policy is PM Gate 1 |
| `GROUP` | selected Family members | explicit title and participant lifecycle |
| `SERVICE` | service channel or Action Messages | never expands a user's Family or service permission |

`conversation_rooms` has `family_group_id`, type, title, status, creator,
timestamps, and soft-close/delete lifecycle. A Family Owner is not implicitly a
reader or manager of all Rooms.

## Participant and message rules

Participants link an Account to a Room, independently of Family Role. A
participant has Room Role (`owner`, `admin`, `member`), status, join/leave
history, and visibility boundary. The sender is always derived from the
authenticated Account, never request data.

Message types are `TEXT`, `SYSTEM`, and `SERVICE_ACTION`. Each message has a
stable ID, Room-local ordering value, `client_message_id`, body/payload,
server-created time, and soft-delete/revision fields. Attachments, reactions,
calls, search, and encryption are explicitly out of scope.

## Proposed v1 policies

- Default deny; inactive Account, Membership, subscription, or participant has
  no Doran authority.
- A new participant sees messages from its `visible_from_sequence` onward.
- A removed participant loses Room access; whether a voluntary leaver can read
  pre-leave history is PM Gate 3.
- Sender may create a visible tombstone through soft delete; hard delete is not
  a v1 operation. Editing is deferred unless PM Gate 4 selects a bounded rule.
- Read state is participant-level and monotonic, not a row per message/user.

See [Data Model](DORAN_DATA_MODEL.md), [Permissions](DORAN_PERMISSION_MATRIX.md),
and [Sync](DORAN_SYNC_AND_WEBSOCKET_CONTRACT.md).

## Evidence durability and fixture isolation

`/tmp/phase1-naran-shell-captures` is temporary evidence; its manifest is the
canonical repository record. Persistent visual diffs, if required, must be
published as redacted Agent System or Drive evidence in a later task.

The Phase 1 QA seed contamination is a prerequisite finding: Doran suites must
use a suite-specific DB, rollback, deterministic reset, or namespace fixtures.
Manual clean seeding is not an acceptable canonical test-isolation contract.

## PM Gates

| Gate | Options | Recommendation | Impact if deferred |
| --- | --- | --- | --- |
| 1. DIRECT duplicate rule | one canonical active pair / allow multiple | one canonical active pair per unordered Account pair and Family | Room-create API stays unimplemented |
| 2. Room ordering allocation | PK only / Room sequence / ULID-time | transaction-safe Room-local sequence with stable `(sequence, id)` cursor | exact concurrent ordering remains undefined |
| 3. History visibility | all history / join-forward / configurable | join-forward via `visible_from_sequence`; removed access denied | voluntary-leave history stays policy-undefined |
| 4. Edit/delete v1 | edit + delete / tombstone only / neither | tombstone delete only; defer edit/revision | no message-edit API in Foundation |
| 5. Unsubscribed history | deny all / read retained / export only | deny send/create, preserve data, permit read only if active participant policy approves | subscription stop behavior must default deny for new activity |

Retention period, account erasure, export, and operating backup policy are
`PM_POLICY_REQUIRED` but are not elevated into an implementation-blocking sixth
gate because no current policy evidence supports a numeric decision.
