"""Board-room duplicate-creation race hardening.

`MONGLE-W7-5-FOCUSED-INDEPENDENT-RE-QA-001` (`RE-QA-F-BOARD-ROOM-RACE`,
HIGH) reproduced 10/10 concurrent first-visits to a Family's reserved board
room (`__family_board__`, see `board_constants.FAMILY_BOARD_ROOM_TITLE`)
creating a separate duplicate room each -- `create_room`'s GROUP branch had
no existing-room check and no `IntegrityError` handling, unlike its own
DIRECT branch. This migration is the DB-invariant half of the fix (the
service-layer atomic get-or-create is a separate, non-migration change in
`app/domains/wagle/service.py`).

Two things happen here, in order, because the unique index below cannot be
added while duplicate rows exist:

1. **Merge**, per Family, any existing duplicate `__family_board__` GROUP
   rooms into one canonical room (earliest `created_at`, tie-broken by
   `id`) with zero loss of message/reaction/comment/member content, and
   without losing a membership's *active* participation semantics:
   - for every membership, the survivor participant row is chosen by
     considering EVERY row across the whole duplicate set (canonical's own
     included, not just loser rows): if an active row exists anywhere, it
     always wins (preferring one already in canonical, else the earliest to
     join) -- an active row in a loser room is never displaced by a stale
     `left` row sitting in canonical. Only when no active row exists
     anywhere does a deterministic terminal (`left`) survivor get chosen
     (canonical's own row first, else the most recently left, else the most
     recently joined). `joined_at` is merged to the earliest across the set;
     `left_at` is cleared to `NULL` when the final state is active, or set
     to the latest `left_at` across the set otherwise. This corrects
     `HARDENING-QA-F-001` (`MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-
     001`): the prior version picked the earliest-`joined_at` *loser* row
     with no active filter, which let a genuinely active loser participant
     lose to an older `left` row whenever canonical already held any row
     for that membership;
   - every message from every duplicate room is re-pointed onto the
     canonical room and globally renumbered by `created_at` (a bare
     sequence copy would collide with the canonical room's own numbers);
     reactions need no change since they key off `message_id`, not
     `room_id`, and follow their message automatically;
   - a promoted participant's `joined_sequence` is reset to 0 (full
     visibility of the merged history) rather than an attempted precise
     recompute -- correct because the only quantity this could hide is a
     board post, and the whole point of this migration is that no board
     post disappears;
   - every participant's own `last_read_sequence` (survivors included, not
     only rows being merged away) is translated from its pre-merge,
     room-local sequence number into the new merged numbering via an
     explicit old-`(room_id, sequence)`-to-new-sequence mapping built while
     renumbering messages, then folded via `GREATEST(...)` -- not a raw
     integer carried over as an approximation, since the same numeric value
     can point at a completely different message after a global renumber;
   - a Service binding on a loser room is re-pointed to the canonical room,
     or dropped if the same Principal is already bound there (the unique
     constraint on `(service_principal_id, room_id)` would otherwise
     collide) -- no board room in this repository's live data has ever had
     a Service binding, so this branch is defensive, not exercised by any
     known real row;
   - the loser room itself is soft-deleted (`deleted_at`), never hard
     deleted -- consistent with `SoftDeleteMixin` everywhere else in this
     domain, and everything that could reference it has already been moved.

   As of this migration's own authoring, the only observed live
   environment (`mongle-db-1` / `mc_festival_phase0`, read-only observation
   only) has **zero** existing duplicate board rooms -- this step is a
   no-op there. It is still required and is exercised against synthetic
   seeded duplicates in a disposable database, not skipped because
   production happens to be clean today.

2. **Invariant**: a partial unique index on `wagle_rooms(family_group_id)`
   scoped to `room_type = 'GROUP' AND title = '__family_board__' AND
   deleted_at IS NULL` -- the reserved-sentinel-only design the Re-QA's own
   remediation guidance recommended as the safe minimal alternative to a
   full `room_key` column, since ordinary (non-reserved-title) GROUP rooms
   must keep being allowed to share a display title.

Verified twice against synthetic seeded duplicates in a dedicated disposable
database. First pass (`MONGLE-W7-5-BOARD-ROOM-RACE-AND-AUTH-HARDENING-001`):
3 rooms, overlapping and non-overlapping memberships, cross-room
`client_message_id` values, reactions, read-states, plus an untouched second
Family as a negative control -- all 4 messages/2 memberships/2 reactions
survived with zero loss. Second pass
(`MONGLE-W7-5-HARDENING-QA-FAIL-REMEDIATION-001`, after the participant-merge
rewrite above): the exact `HARDENING-QA-F-001` reproduction shape (canonical
`left`, loser older-`left`-then-newer-`active`) plus an ordinary untouched
membership and a cross-room-duplicated membership, in the same seeded
Family -- the previously-lost membership now survives `active` with
`left_at IS NULL`, all 4 messages/2 reactions/3 read-states (translated into
the merged sequence numbering, not stale raw integers) survived, and the
untouched second Family stayed byte-for-byte unchanged. Both passes:
`downgrade()` cleanly dropped only the index (data stayed merged, as
documented above) and re-`upgrade()` recreated the index with zero errors (0
duplicates remained to conflict with it). The 10-case regression matrix in
`backend/tests/test_migration_0021_participant_merge.py` covers this
algorithm permanently, including one test that independently confirmed
(against a throwaway copy of the pre-remediation algorithm, then rolled
back) that the old code produced exactly the `{left: 2, active: 0}` result
`HARDENING-QA-F-001` reported.

Known, accepted limitation: if two duplicate rooms' messages would collide on
`uq_wagle_messages_sender_client` after the sender remap, the merge fails
loud on that constraint rather than silently dropping one -- a genuine data
ambiguity for a human to resolve, not something this migration guesses
about; no observed data (real or synthetic) has ever hit it.

Revision ID: 0021_board_room_race_hardening
Revises: 0020_wagle_message_reactions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "0021_board_room_race_hardening"
down_revision = "0020_wagle_message_reactions"
branch_labels = None
depends_on = None

FAMILY_BOARD_ROOM_TITLE = "__family_board__"

_UNIQUE_INDEX_NAME = "uq_wagle_rooms_family_board_singleton"


def _merge_duplicate_board_rooms(bind) -> None:
    duplicate_families = bind.execute(
        text(
            """
            SELECT family_group_id
            FROM wagle_rooms
            WHERE title = :title AND room_type = 'GROUP' AND deleted_at IS NULL
            GROUP BY family_group_id
            HAVING count(*) > 1
            """
        ),
        {"title": FAMILY_BOARD_ROOM_TITLE},
    ).scalars().all()

    for family_id in duplicate_families:
        room_ids = bind.execute(
            text(
                """
                SELECT id FROM wagle_rooms
                WHERE family_group_id = :family_id AND title = :title
                  AND room_type = 'GROUP' AND deleted_at IS NULL
                ORDER BY created_at ASC, id ASC
                """
            ),
            {"family_id": family_id, "title": FAMILY_BOARD_ROOM_TITLE},
        ).scalars().all()
        canonical_id = room_ids[0]
        loser_ids = room_ids[1:]

        # --- Phase 1: decide exactly one canonical participant row per
        # membership, considering EVERY row across the whole duplicate set
        # (canonical's own rows included) -- not just loser rows. The
        # earlier version of this migration only ever picked among loser
        # rows, ordered by joined_at with no status filter, which let a
        # membership's genuinely *active* row lose to an older *left* row
        # whenever canonical itself already held a (non-active) row for that
        # membership (HARDENING-QA-F-001: canonical `left` + loser
        # older-`left`-then-newer-`active` produced 0 active survivors).
        # Rule, matching the task's own stated priority: ACTIVE beats LEFT,
        # always, regardless of which room (canonical or loser) holds it.
        membership_ids = bind.execute(
            text(
                "SELECT DISTINCT family_membership_id FROM wagle_participants WHERE room_id IN :room_ids"
            ).bindparams(sa.bindparam("room_ids", expanding=True)),
            {"room_ids": room_ids},
        ).scalars().all()

        participant_map: dict = {}  # old (non-survivor) participant id -> survivor id
        participant_home_room: dict = {}  # every participant id (survivor included) -> its pre-merge room_id
        survivor_ids: set = set()

        for membership_id in membership_ids:
            all_rows = bind.execute(
                text(
                    "SELECT id, room_id FROM wagle_participants WHERE room_id IN :room_ids AND family_membership_id = :membership_id"
                ).bindparams(sa.bindparam("room_ids", expanding=True)),
                {"room_ids": room_ids, "membership_id": membership_id},
            ).mappings().all()
            if not all_rows:
                continue
            for row in all_rows:
                participant_home_room[row["id"]] = row["room_id"]

            # Active-row survivor, if any exists anywhere in the set: prefer
            # one already sitting in canonical, else the earliest to join.
            survivor_id = bind.execute(
                text(
                    """
                    SELECT id FROM wagle_participants
                    WHERE room_id IN :room_ids AND family_membership_id = :membership_id AND status = 'active'
                    ORDER BY (room_id = :canonical_id) DESC, joined_at ASC NULLS LAST, id ASC
                    LIMIT 1
                    """
                ).bindparams(sa.bindparam("room_ids", expanding=True)),
                {"room_ids": room_ids, "membership_id": membership_id, "canonical_id": canonical_id},
            ).scalars().first()

            if survivor_id is not None:
                target_left_at = None  # final state is active -- never a stale left_at
            else:
                # No active row anywhere for this membership: a deterministic
                # terminal (left/removed) survivor -- prefer canonical's own
                # row, else the most recently left, else the most recently
                # joined, else a stable id tiebreak.
                survivor_id = bind.execute(
                    text(
                        """
                        SELECT id FROM wagle_participants
                        WHERE room_id IN :room_ids AND family_membership_id = :membership_id
                        ORDER BY (room_id = :canonical_id) DESC, left_at DESC NULLS LAST, joined_at DESC NULLS LAST, id ASC
                        LIMIT 1
                        """
                    ).bindparams(sa.bindparam("room_ids", expanding=True)),
                    {"room_ids": room_ids, "membership_id": membership_id, "canonical_id": canonical_id},
                ).scalars().first()
                target_left_at = bind.execute(
                    text(
                        "SELECT MAX(left_at) FROM wagle_participants WHERE room_id IN :room_ids AND family_membership_id = :membership_id"
                    ).bindparams(sa.bindparam("room_ids", expanding=True)),
                    {"room_ids": room_ids, "membership_id": membership_id},
                ).scalar_one()

            earliest_joined_at = bind.execute(
                text(
                    "SELECT MIN(joined_at) FROM wagle_participants WHERE room_id IN :room_ids AND family_membership_id = :membership_id"
                ).bindparams(sa.bindparam("room_ids", expanding=True)),
                {"room_ids": room_ids, "membership_id": membership_id},
            ).scalar_one()

            survivor_ids.add(survivor_id)
            bind.execute(
                text(
                    "UPDATE wagle_participants SET room_id = :canonical_id, joined_sequence = 0, "
                    "joined_at = COALESCE(:earliest_joined_at, joined_at), left_at = :target_left_at "
                    "WHERE id = :pid"
                ),
                {
                    "canonical_id": canonical_id,
                    "earliest_joined_at": earliest_joined_at,
                    "target_left_at": target_left_at,
                    "pid": survivor_id,
                },
            )
            for row in all_rows:
                if row["id"] != survivor_id:
                    participant_map[row["id"]] = survivor_id

        # --- Phase 2: messages -- remap sender to survivor, re-point to
        # canonical, then renumber. (Sender remap must happen before
        # deleting merged-away participant rows below --
        # wagle_messages.sender_participant_id is ON DELETE RESTRICT.) A
        # bulk room_id re-point collides immediately against
        # uq_wagle_messages_room_sequence the moment two rooms' messages
        # share a sequence number (near-certain: every room starts counting
        # from 1). Two single-row passes avoid that: first move every
        # message (canonical's own included) onto a unique *negative*
        # temporary sequence -- a value no real message ever holds, so no
        # intermediate row-by-row step can collide -- then assign the real
        # ascending 1..N sequence in a second pass once nothing positive
        # remains to collide with. The pre-merge (room_id, sequence) of every
        # message is captured here so read-states (phase 3) can be
        # translated into the same new numbering instead of keeping a stale
        # raw integer that no longer points at the same message.
        message_rows = bind.execute(
            text(
                "SELECT id, room_id, sequence FROM wagle_messages WHERE room_id IN :room_ids "
                "ORDER BY created_at ASC, sequence ASC, id ASC"
            ).bindparams(sa.bindparam("room_ids", expanding=True)),
            {"room_ids": room_ids},
        ).mappings().all()

        for old_pid, survivor_pid in participant_map.items():
            bind.execute(
                text(
                    "UPDATE wagle_messages SET sender_participant_id = :survivor_pid WHERE sender_participant_id = :old_pid"
                ),
                {"survivor_pid": survivor_pid, "old_pid": old_pid},
            )

        for temp_index, row in enumerate(message_rows, start=1):
            bind.execute(
                text("UPDATE wagle_messages SET room_id = :canonical_id, sequence = :temp_seq WHERE id = :mid"),
                {"canonical_id": canonical_id, "temp_seq": -temp_index, "mid": row["id"]},
            )

        # Second pass: every message currently holds a unique negative temp
        # sequence (see above), so assigning the real ascending 1..N in the
        # same already-computed created_at order cannot collide with any
        # not-yet-processed row (still negative) or any already-processed one
        # (strictly smaller).
        old_to_new_sequence: dict = {}  # (pre-merge room_id, pre-merge sequence) -> new sequence
        new_sequence = 0
        for row in message_rows:
            new_sequence += 1
            old_to_new_sequence[(row["room_id"], row["sequence"])] = new_sequence
            bind.execute(
                text("UPDATE wagle_messages SET sequence = :seq WHERE id = :mid"),
                {"seq": new_sequence, "mid": row["id"]},
            )
        bind.execute(
            text("UPDATE wagle_rooms SET next_message_sequence = :next_seq WHERE id = :canonical_id"),
            {"next_seq": new_sequence + 1, "canonical_id": canonical_id},
        )

        # --- Phase 3: read-states -- translate each participant's own
        # pre-merge (room-local) last_read_sequence into the new merged
        # numbering via the mapping built above, rather than folding a raw
        # integer that no longer corresponds to the same message. This
        # applies to survivors too (a survivor's own room may have just been
        # renumbered along with everyone else's), not only to rows being
        # merged away.
        def _translate_read_sequence(participant_id, old_value) -> int:
            if not old_value:
                return 0
            home_room = participant_home_room.get(participant_id)
            translated = old_to_new_sequence.get((home_room, old_value))
            if translated is not None:
                return translated
            # The cursor pointed at a sequence number with no exact match in
            # the mapping (e.g. past that room's own last real message) --
            # clamp to the highest new sequence actually reached by that
            # room's own pre-merge messages at or before this cursor, rather
            # than silently keeping a meaningless raw integer or regressing
            # to 0 (a false "unread everything").
            candidates = [
                new_seq for (room_id, old_seq), new_seq in old_to_new_sequence.items()
                if room_id == home_room and old_seq <= old_value
            ]
            return max(candidates) if candidates else 0

        for survivor_pid in survivor_ids:
            own_old_value = bind.execute(
                text("SELECT last_read_sequence FROM wagle_participant_read_states WHERE participant_id = :pid"),
                {"pid": survivor_pid},
            ).scalars().first()
            if own_old_value is not None:
                translated = _translate_read_sequence(survivor_pid, own_old_value)
                bind.execute(
                    text("UPDATE wagle_participant_read_states SET last_read_sequence = :v WHERE participant_id = :pid"),
                    {"v": translated, "pid": survivor_pid},
                )

        for old_pid, survivor_pid in participant_map.items():
            old_value = bind.execute(
                text("SELECT last_read_sequence FROM wagle_participant_read_states WHERE participant_id = :pid"),
                {"pid": old_pid},
            ).scalars().first()
            translated = _translate_read_sequence(old_pid, old_value) if old_value is not None else 0
            bind.execute(
                text(
                    """
                    INSERT INTO wagle_participant_read_states (participant_id, last_read_sequence)
                    VALUES (:survivor_pid, :translated)
                    ON CONFLICT (participant_id) DO UPDATE SET last_read_sequence = GREATEST(
                        wagle_participant_read_states.last_read_sequence, EXCLUDED.last_read_sequence
                    )
                    """
                ),
                {"survivor_pid": survivor_pid, "translated": translated},
            )
            bind.execute(
                text("DELETE FROM wagle_participant_read_states WHERE participant_id = :old_pid"),
                {"old_pid": old_pid},
            )
            bind.execute(text("DELETE FROM wagle_participants WHERE id = :old_pid"), {"old_pid": old_pid})

        # --- Service bindings: re-point, or drop on collision ---
        loser_bindings = bind.execute(
            text(
                "SELECT id, service_principal_id FROM wagle_service_bindings WHERE room_id IN :loser_ids"
            ).bindparams(sa.bindparam("loser_ids", expanding=True)),
            {"loser_ids": loser_ids},
        ).mappings().all()
        for row in loser_bindings:
            collision = bind.execute(
                text(
                    "SELECT 1 FROM wagle_service_bindings WHERE room_id = :canonical_id AND service_principal_id = :pid"
                ),
                {"canonical_id": canonical_id, "pid": row["service_principal_id"]},
            ).scalars().first()
            if collision:
                bind.execute(text("DELETE FROM wagle_service_bindings WHERE id = :bid"), {"bid": row["id"]})
            else:
                bind.execute(
                    text("UPDATE wagle_service_bindings SET room_id = :canonical_id WHERE id = :bid"),
                    {"canonical_id": canonical_id, "bid": row["id"]},
                )

        # --- Loser rooms: soft-delete, never hard-delete ---
        bind.execute(
            text(
                "UPDATE wagle_rooms SET deleted_at = now() WHERE id IN :loser_ids"
            ).bindparams(sa.bindparam("loser_ids", expanding=True)),
            {"loser_ids": loser_ids},
        )


def upgrade() -> None:
    bind = op.get_bind()
    _merge_duplicate_board_rooms(bind)
    op.create_index(
        _UNIQUE_INDEX_NAME,
        "wagle_rooms",
        ["family_group_id"],
        unique=True,
        postgresql_where=sa.text(
            f"room_type = 'GROUP' AND title = '{FAMILY_BOARD_ROOM_TITLE}' AND deleted_at IS NULL"
        ),
    )


def downgrade() -> None:
    # Reverses the schema invariant only. The duplicate merge performed by
    # upgrade() is a one-time data consolidation, not a reversible schema
    # change -- merged rooms/messages/participants are not un-merged, the
    # same convention every irreversible data-bearing step in this migration
    # history follows (e.g. 0007's service-code renames). Nothing here
    # deletes or loses data; it only removes the constraint that prevents a
    # fresh duplicate from being created again.
    op.drop_index(_UNIQUE_INDEX_NAME, table_name="wagle_rooms")
