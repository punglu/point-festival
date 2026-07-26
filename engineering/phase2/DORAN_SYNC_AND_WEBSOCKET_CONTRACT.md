# Doran Sync and WebSocket Contract

**Status:** APPROVED FOUNDATION HTTP CONTRACT / HTTP and database remain canonical; no WebSocket is implemented.

## HTTP candidate surface

```text
GET/POST  /api/families/{family_id}/doran/rooms
GET/PATCH /api/families/{family_id}/doran/rooms/{room_id}
GET/POST  /api/families/{family_id}/doran/rooms/{room_id}/participants
DELETE    /api/families/{family_id}/doran/rooms/{room_id}/participants/{participant_id}
GET/POST  /api/families/{family_id}/doran/rooms/{room_id}/messages
DELETE    /api/families/{family_id}/doran/rooms/{room_id}/messages/{message_id}
PUT       /api/families/{family_id}/doran/rooms/{room_id}/read-state
```

Lists use `{items, total, cursor?}` and a sequence cursor. `after_sequence` and
`before_sequence` are mutually exclusive; initial requests return latest-N,
`before_sequence` pages history, and `after_sequence` synchronizes reconnects.
Every path first
authenticates Account, resolves active Membership, checks subscription and
permission, then checks resource Family and active Room participant.

## Event envelope

```json
{"type":"message.created","version":1,"event_id":"uuid","room_id":42,
 "sequence":123,"occurred_at":"ISO-8601","payload":{}}
```

Allowed target events: `message.created`, `message.updated`,
`message.deleted`, `read_state.updated`, `participant.joined`,
`participant.left`, and `room.updated`. Clients deduplicate by `event_id` and
apply only newer Room sequence state. Events are delivery hints, never the sole
write acknowledgement.

## Reconnect algorithm

```text
save highest observed room sequence
→ reconnect and authenticate Account
→ HTTP GET messages?after_sequence=cursor
→ merge idempotently by event ID / message ID / sequence
→ subscribe to permitted Room stream
```

During HTTP sync and live delivery, reducer state must tolerate duplicate and
out-of-order events. Revoked Membership/participant or expired token ends or
denies subscription. A Family switch clears room cache before subscribing in
the new Family.

## Push boundary

Push is auxiliary delivery, not a message read API. Default payload contains
opaque context, notification type, room ID, and message ID—not sensitive body.
On open, client rechecks authorization via HTTP. Device/session registration,
Push sending, and badge delivery are later work.
