# Doran Legacy 1:1 Migration Plan

**Status:** TARGET PLAN / no operating migration is authorized.

Legacy `chat_messages` uses Player sender/receiver IDs, message text, read
boolean, created time, soft-delete mixin, and pair history queries. It has no
Family or Account proof, so it cannot be automatically promoted to Doran.

## Candidate procedure

1. Back up and schema-compare under the operating Human Gate.
2. Produce a read-only inventory: row counts, sender/receiver pairs, deleted
   players, missing mappings, duplicate candidates, and orphan rows.
3. Only for a reviewed pair whose two Player identities map to Accounts in the
   same reviewed Family, create one `DIRECT` Room according to the duplicate
   Room policy.
4. Import messages in stable `(created_at, legacy_id)` order with an explicit
   legacy-origin mapping/checksum; preserve soft-delete semantics.
5. Do not infer identity from names/usernames. Do not import cross-Family,
   unmapped, ambiguous, or orphan messages automatically; emit a Human Review
   report instead.
6. Validate counts, checksums, ordering, and sampled visibility before a
   dual-read adapter or cutover. Keep rollback point and legacy read path until
   acceptance.

Read-state migration is approximate: legacy has a receiver-side boolean per
message, while Doran has a monotonic participant cursor. Build a candidate
cursor only when the historical sequence is complete; otherwise retain unread
as unknown/recompute safely. Never advance a read cursor merely to make data
look complete.
