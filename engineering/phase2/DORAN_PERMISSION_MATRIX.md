# Doran Permission Matrix

**Status:** TARGET / extends the approved Permission namespace only after PM review.

| Action | Family role | Service role / resource condition | Backend control |
| --- | --- | --- | --- |
| List/read own Room history | baseline participation | active Doran subscription + active participant + `messaging.messages.read` | Family, Room, Participant cross-check |
| Send message | baseline participation | active participant + `messaging.messages.send` | sender derived from Account |
| Create Room | owner/admin; member is PM Gate | `messaging.rooms.create` | all invitees active in same Family |
| Add/remove participant | owner/admin or delegated room admin | `messaging.participants.manage` | no cross-Family Account or participant substitution |
| Update Room metadata | creator/Room admin as policy permits | `messaging.rooms.manage` | Room Role, not Family Owner by default |
| Read another Room | deny | no implicit Family-admin override | participant visibility required |
| Service Action Message | service actor only | active subscription and allow-listed payload | service payload cannot grant authority |

Proposed minimum permission candidates:

```text
messaging.messages.read
messaging.messages.send
messaging.rooms.create
messaging.rooms.manage
messaging.participants.manage
```

`messaging.participate` remains a high-level eligibility permission. Role
mapping is intentionally deferred: `room_admin` may delegate room management;
`participant` conveys only explicitly mapped messaging permissions. Role
strings are never used by frontend or backend as an authorization shortcut.

Subscription stop recommendation: preserve data, deny new Room creation and
send, and make continued history reading a PM Gate. No automatic deletion.
