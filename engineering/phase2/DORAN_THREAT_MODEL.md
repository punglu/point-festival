# Doran Threat Model and Test Matrix

| Threat | Backend control | Required implementation test |
| --- | --- | --- |
| Family/Room/participant ID substitution | Membership + resource Family + active participant guard | cross-Family and nonparticipant read/write denied; DB unchanged |
| Sender ID spoofing | derive sender from Account | body sender ignored; stored sender is caller |
| Duplicate mobile retry | scoped client-message unique invariant | repeat returns existing result; changed payload conflicts |
| Ordering loss/reversal | canonical Room sequence | concurrent sends and cursor order deterministic |
| Read-state rollback or substitution | participant-owned monotonic max update | other participant denied; older cursor cannot regress |
| WebSocket cross-room/family event | authenticated scoped subscription | unauthorized subscribe denied; revoke disconnect/sync denial |
| Stale role/subscription | evaluate current DB state | stopped subscription cannot send/create |
| Delete/revision resurrection | immutable event/audit rules | tombstone remains; unauthorized restore denied |
| Service Action forgery | allow-list payload/version and target API authorization | payload cannot execute unpermitted service action |
| Legacy wrong-Family import | reviewed identity + Family mapping | ambiguous/orphan/cross-Family rows skipped and reported |
| Push disclosure | minimal payload and re-fetch authorization | payload excludes message body; revoked client cannot fetch |

See [Implementation Plan](DORAN_IMPLEMENTATION_PLAN.md) for API+DB, WebSocket,
and migration test packages. The future implementation is independent-QA
mandatory because it changes schema, authorization, realtime state, and data.
