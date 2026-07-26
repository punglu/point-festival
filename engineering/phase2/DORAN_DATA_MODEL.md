# Doran Data Model

**Status:** TARGET / no migration or schema change in this task.

```text
FamilyGroup 1 ── * ConversationRoom 1 ── * ConversationParticipant * ── 1 Account
                                     │
                                     └── * Message
ConversationParticipant 1 ── 1 ParticipantReadState
Message 1 ── * MessageRevision (only if edit policy is approved)
```

| Target table | Responsibility | Key invariants |
| --- | --- | --- |
| `conversation_rooms` | Family-scoped room lifecycle | Room has one Family; active `DIRECT` has exactly two active participants |
| `conversation_participants` | Account's Room relation | one active relation per `(room_id, account_id)`; room role is not Family Role |
| `messages` | canonical durable message | sender is active participant; `(sender_account_id, room_id, client_message_id)` unique |
| `participant_read_states` | furthest read position | one per participant; cursor only moves forward |
| `message_revisions` | optional edit audit | no v1 table unless PM approves editing |

## Essential fields

`conversation_rooms`: `id`, `family_group_id`, `room_type`, `title`, `status`,
`created_by_account_id`, `created_at`, `updated_at`, `closed_at`, `deleted_at`.

`conversation_participants`: `id`, `room_id`, `account_id`, `participant_role`,
`status`, `joined_at`, `left_at`, `visible_from_sequence`, notification preference.

`messages`: `id`, `room_id`, `sequence_number`, `sender_account_id`,
`message_type`, `client_message_id`, body, `created_at`, `edited_at`,
`deleted_at`, optional reply and service payload metadata.

`participant_read_states`: `participant_id`, `last_read_sequence`,
`updated_at`. Updates use `max(existing, requested)` inside the use-case UoW.

## Ordering and cursor

Recommended target is a Room-local monotonic `sequence_number`, backed by a
unique `(room_id, sequence_number)` index. Database insertion, not WebSocket
arrival, is canonical ordering. Cursor lists use `(sequence_number, id)` to
remain deterministic. The allocation mechanism is PM Gate 2: a locked Room
counter or equivalent transaction-safe PostgreSQL approach must be selected in
implementation.

## Lifecycle and retention

Soft deletion preserves audit and cursor continuity; client rendering uses a
tombstone. Retention duration, export, backup, Account deletion, and voluntary
leave-history treatment are `PM_POLICY_REQUIRED`; no number is invented here.

Legacy rows are not renamed or altered. See [Legacy Migration Plan](DORAN_LEGACY_MIGRATION_PLAN.md).
