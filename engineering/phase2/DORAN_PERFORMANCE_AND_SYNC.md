# Doran Performance and Sync Contract R2

**Status:** APPROVED CONTRACT / canonical R2 (2026-07-26)
**Authority:** complements [DORAN_MESSAGING_CONTRACT.md](DORAN_MESSAGING_CONTRACT.md). HTTP/DB remains canonical; realtime is an auxiliary future delivery path.

## Cursor and HTTP synchronization

Message order is stable `(sequence, message_id)`, with Room-local server
sequence as the primary ordering value. Timestamps are display metadata, never
a cursor or ordering authority.

| Request form | Purpose | Contract |
| --- | --- | --- |
| no cursor | initial recent window | return the most recent bounded page in ascending display order |
| `before_sequence` | older history | return only visible sequences before the cursor |
| `after_sequence` | reconnect/incremental sync | return only visible sequences after the cursor |

`before_sequence` and `after_sequence` are mutually exclusive. A response must
include the returned range and `has_more_before` / `has_more_after`, without
requiring an expensive exact total. Cursor, limit, and Room mismatch are
validated; a current authorization check is required even for a previously valid
cursor. Tombstones retain sequence, so pages neither duplicate nor silently skip
the deleted logical message.

R2-A configuration defaults are TEXT body maximum 4,000 characters, message
page default 50/maximum 100, GROUP Participant maximum 50, and
`client_message_id` maximum 64 characters. Rate-limit, WebSocket, event-payload,
and connection values are R2-B/Realtime measurement work. They cannot be left
unbounded when those endpoints are introduced.

## Realtime boundary

WebSocket does not replace HTTP/DB source of truth. Before implementation it
requires a short-lived ticket, Origin allowlist, authenticated connect, Room and
Participant recheck for every message/action, immediate revoke after relevant
Family/Participant state change, cursor catch-up, duplicate defence, batching,
backpressure, connection/frame/rate limits, and safe reconnect behavior.

WebSocket, Push, Service Worker, and delivery broker are **NOT IMPLEMENTED /
DEFERRED**. A reconnect obtains incremental state from the server cursor rather
than reloading the entire Room or trusting client sender/sequence/permission
claims.

## Conversation accumulation performance contract

The future client must not retain an unlimited Room history in DOM or memory.

- Initial entry fetches only a recent bounded window; older pages load on demand.
- The message timeline uses virtualization/windowing and removes offscreen
  message DOM.
- Per-Room and total cached pages have approved caps, eviction, and refetch
  behavior.
- Inserting older pages maintains the user's scroll anchor; variable-height
  messages, images, and late layout changes must not cause uncontrolled jumps.
- Images, attachments, and link previews are lazy; offscreen media work is
  cancelled when no longer needed. Attachments themselves remain outside v1
  Foundation until separately contracted.
- A user viewing history is not forced to the bottom by new messages; the UI
  exposes new-message indication and an explicit return-to-latest action.
- Room exit cleans listeners, observers, media, timers, and temporary state.
- Incoming events are deduplicated and sequence-sorted with concurrently loaded
  history. Tombstones, date separators, unread marker/read state, reply target,
  deep links, and future search navigation remain coherent under virtualization.

Mobile behavior includes iOS viewport and keyboard changes, safe area, Android
system Back, orientation changes, and restoration without retaining stale Room
DOM.

## Performance QA contract

Before frontend delivery, test with large synthetic message fixtures, repeated
Room switching, history/latest scroll cycles, long-running receipt, reconnect
merge, duplicate/missing-event injection, low-end mobile viewport, variable
height content, and image load changes. Record DOM-node upper bounds, heap
growth and recovery, scroll-anchor displacement, event batch/backpressure
behavior, and console errors under environment-approved thresholds.

The completed Mongle Shell DOM audit is not evidence of Doran conversation
performance: it measured the current Shell, not a Doran message timeline.

## Current delivery state

Cursor-backed HTTP semantics are an R2-A requirement. Virtualized UI, cache
eviction, media lifecycle, realtime transport, and their load QA are **DEFERRED
/ NOT IMPLEMENTED**. No performance claim is implied by this contract alone.
