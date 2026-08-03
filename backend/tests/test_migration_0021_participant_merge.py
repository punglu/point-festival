"""Migration-level regression matrix for `0021_board_room_race_hardening`'s
participant-merge algorithm, against real PostgreSQL.

`MONGLE-W7-5-HARDENING-FOCUSED-INDEPENDENT-QA-001` (verdict `FAIL`) found
`HARDENING-QA-F-001`: the merge picked the earliest-`joined_at` *loser* row
as survivor with no `status` filter, so a genuinely `active` loser row could
lose to an older `left` row already sitting in canonical -- reproduced as
canonical `left` + loser (older `left`, newer `active`) -> 0 active
survivors after merge. The migration's `_merge_duplicate_board_rooms` was
rewritten to consider every row across the whole duplicate set (canonical's
own included) and let `active` win regardless of which room holds it; these
tests exercise that directly against the real merge function and a real
database, not a mock.

The unique index the migration itself adds
(`uq_wagle_rooms_family_board_singleton`) would block seeding duplicate rows
directly, since every disposable test database already has migration `0021`
applied (`alembic upgrade head` runs before pytest per `tests/README.md`).
Each test therefore drops that one index for its own duration only (fixture
`board_singleton_index_dropped`, restored in a `finally` so no other test in
the suite -- e.g. `test_wagle_integration.py`'s own concurrency regression --
loses the real constraint), seeds a pre-migration-shaped duplicate scenario,
invokes the migration's own `_merge_duplicate_board_rooms` function through
`AsyncConnection.run_sync` (the same async/sync bridge Alembic's own
`env.py` uses), and asserts the resulting rows directly.
"""
from __future__ import annotations

import importlib.util
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest_asyncio
from sqlalchemy import text

from tests.conftest import create_bare_membership, create_family

_MIGRATION_PATH = (
    Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0021_board_room_race_hardening.py"
)
_spec = importlib.util.spec_from_file_location("migration_0021_under_test", _MIGRATION_PATH)
migration_0021 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration_0021)

BOARD_TITLE = migration_0021.FAMILY_BOARD_ROOM_TITLE
UNIQUE_INDEX_NAME = migration_0021._UNIQUE_INDEX_NAME


@pytest_asyncio.fixture
async def board_singleton_index_dropped(db):
    await db.execute(text(f"DROP INDEX IF EXISTS {UNIQUE_INDEX_NAME}"))
    await db.commit()
    try:
        yield
    finally:
        await db.execute(
            text(
                f"CREATE UNIQUE INDEX {UNIQUE_INDEX_NAME} ON wagle_rooms (family_group_id) "
                f"WHERE room_type = 'GROUP' AND title = '{BOARD_TITLE}' AND deleted_at IS NULL"
            )
        )
        await db.commit()


async def _make_room(db, family_id: int, created_at: datetime) -> uuid.UUID:
    room_id = (
        await db.execute(
            text(
                "INSERT INTO wagle_rooms (family_group_id, room_type, title, status, "
                "created_by_actor_type, created_at, updated_at) "
                "VALUES (:f, 'GROUP', :title, 'active', 'ACCOUNT', :ts, :ts) RETURNING id"
            ),
            {"f": family_id, "title": BOARD_TITLE, "ts": created_at},
        )
    ).scalar_one()
    return room_id


async def _add_participant(db, family_id: int, room_id, membership_id: int, *, status: str, joined_at: datetime, left_at: datetime | None = None):
    return (
        await db.execute(
            text(
                "INSERT INTO wagle_participants (family_group_id, room_id, family_membership_id, room_role, "
                "status, joined_sequence, joined_at, left_at) "
                "VALUES (:f, :r, :m, 'member', :status, 0, :joined_at, :left_at) RETURNING id"
            ),
            {"f": family_id, "r": room_id, "m": membership_id, "status": status, "joined_at": joined_at, "left_at": left_at},
        )
    ).scalar_one()


async def _add_message(db, family_id: int, room_id, participant_id, sequence: int, body: str, created_at: datetime):
    mid = (
        await db.execute(
            text(
                "INSERT INTO wagle_messages (family_group_id, room_id, sequence, sender_participant_id, "
                "message_type, body, created_at) VALUES (:f, :r, :seq, :p, 'TEXT', :body, :ts) RETURNING id"
            ),
            {"f": family_id, "r": room_id, "seq": sequence, "p": participant_id, "body": body, "ts": created_at},
        )
    ).scalar_one()
    await db.execute(text("UPDATE wagle_rooms SET next_message_sequence = :n WHERE id = :r"), {"n": sequence + 1, "r": room_id})
    return mid


async def _set_read_state(db, participant_id, last_read_sequence: int):
    await db.execute(
        text("INSERT INTO wagle_participant_read_states (participant_id, last_read_sequence) VALUES (:p, :v)"),
        {"p": participant_id, "v": last_read_sequence},
    )


async def _run_merge(db):
    await db.commit()
    conn = await db.connection()
    await conn.run_sync(lambda sync_conn: migration_0021._merge_duplicate_board_rooms(sync_conn))
    await db.commit()


async def _participants_for_membership(db, family_id: int, membership_id: int):
    rows = (
        await db.execute(
            text(
                "SELECT p.id, p.room_id, p.status, p.joined_at, p.left_at FROM wagle_participants p "
                "JOIN wagle_rooms r ON r.id = p.room_id "
                "WHERE r.family_group_id = :f AND r.title = :title AND p.family_membership_id = :m"
            ),
            {"f": family_id, "title": BOARD_TITLE, "m": membership_id},
        )
    ).mappings().all()
    return rows


async def _active_board_room_count(db, family_id: int) -> int:
    return (
        await db.execute(
            text(
                "SELECT count(*) FROM wagle_rooms WHERE family_group_id = :f AND title = :title "
                "AND room_type = 'GROUP' AND deleted_at IS NULL"
            ),
            {"f": family_id, "title": BOARD_TITLE},
        )
    ).scalar_one()


NOW = datetime(2026, 8, 1, tzinfo=timezone.utc)


async def test_case1_canonical_active_loser_active_one_survivor_stays_active(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case1")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    await _add_participant(db, family_id, canonical, membership_id, status="active", joined_at=NOW)
    await _add_participant(db, family_id, loser, membership_id, status="active", joined_at=NOW + timedelta(seconds=1))
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "active"
    assert await _active_board_room_count(db, family_id) == 1


async def test_case2_canonical_active_loser_left_stays_active(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case2")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    await _add_participant(db, family_id, canonical, membership_id, status="active", joined_at=NOW)
    await _add_participant(db, family_id, loser, membership_id, status="left", joined_at=NOW - timedelta(days=1), left_at=NOW - timedelta(hours=1))
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "active"
    assert rows[0]["left_at"] is None


async def test_case3_canonical_left_loser_active_promotes_to_active(db, board_singleton_index_dropped):
    """Independently confirmed against the pre-remediation algorithm: this
    single-candidate shape (loser has exactly one row) did not lose the
    active row outright, but left canonical's own stale `left` row
    untouched and unmerged -- a membership-duplication defect (2 rows for 1
    membership) distinct from, but in the same family as, the more severe
    `HARDENING-QA-F-001` reproduction in Case 7 below (where the *complete
    loss* of any active row was independently confirmed against the old
    algorithm)."""
    family_id = await create_family(db, "Case3")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    await _add_participant(db, family_id, canonical, membership_id, status="left", joined_at=NOW - timedelta(days=2), left_at=NOW - timedelta(days=1))
    await _add_participant(db, family_id, loser, membership_id, status="active", joined_at=NOW)
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "active", "active must not be displaced by canonical's stale left row"
    assert rows[0]["left_at"] is None
    assert rows[0]["room_id"] == canonical


async def test_case4_canonical_left_loser_left_stays_left(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case4")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    await _add_participant(db, family_id, canonical, membership_id, status="left", joined_at=NOW - timedelta(days=2), left_at=NOW - timedelta(days=1))
    await _add_participant(db, family_id, loser, membership_id, status="left", joined_at=NOW - timedelta(days=3), left_at=NOW - timedelta(hours=1))
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "left"
    # left_at merges to the latest across the set (the loser's more recent departure)
    assert rows[0]["left_at"] == NOW - timedelta(hours=1)


async def test_case5_no_canonical_participant_one_loser_active(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case5")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    await _add_participant(db, family_id, loser, membership_id, status="active", joined_at=NOW)
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "active"
    assert rows[0]["room_id"] == canonical


async def test_case6_no_canonical_participant_multiple_loser_active(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case6")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical = await _make_room(db, family_id, NOW)
    loser1 = await _make_room(db, family_id, NOW + timedelta(seconds=1))
    loser2 = await _make_room(db, family_id, NOW + timedelta(seconds=2))
    await _add_participant(db, family_id, loser1, membership_id, status="active", joined_at=NOW + timedelta(seconds=5))
    await _add_participant(db, family_id, loser2, membership_id, status="active", joined_at=NOW + timedelta(seconds=1))
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "active"
    assert rows[0]["joined_at"] == NOW + timedelta(seconds=1), "earliest join time across the set is preserved"


async def test_case7_canonical_left_loser_older_left_and_newer_active(db, board_singleton_index_dropped):
    """The Independent QA's own described reproduction shape, 3 rows total.
    Independently confirmed against the pre-remediation algorithm (a
    throwaway copy of the original function, run against this exact seeded
    shape, then rolled back): it produced `{left: 2, active: 0}`, matching
    `HARDENING-QA-F-001`'s own reported evidence verbatim. The old code's
    loser-only, unfiltered-by-status `ORDER BY joined_at ASC` picked the
    *older left* row as survivor and deleted the *active* one entirely."""
    family_id = await create_family(db, "Case7")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    await _add_participant(db, family_id, canonical, membership_id, status="left", joined_at=NOW - timedelta(days=5), left_at=NOW - timedelta(days=4))
    await _add_participant(db, family_id, loser, membership_id, status="left", joined_at=NOW - timedelta(days=3), left_at=NOW - timedelta(days=2))
    await _add_participant(db, family_id, loser, membership_id, status="active", joined_at=NOW - timedelta(days=1))
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "active"
    assert rows[0]["left_at"] is None


async def test_case8_multiple_active_different_read_states_merge_to_max(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case8")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical, loser = await _make_room(db, family_id, NOW), await _make_room(db, family_id, NOW + timedelta(seconds=1))
    p_canonical = await _add_participant(db, family_id, canonical, membership_id, status="active", joined_at=NOW)
    p_loser = await _add_participant(db, family_id, loser, membership_id, status="active", joined_at=NOW + timedelta(seconds=1))
    # canonical: 1 message (read up to it); loser: 2 messages sent after canonical's (read up to its own 2nd)
    await _add_message(db, family_id, canonical, p_canonical, 1, "c1", NOW + timedelta(seconds=2))
    await _add_message(db, family_id, loser, p_loser, 1, "l1", NOW + timedelta(seconds=3))
    await _add_message(db, family_id, loser, p_loser, 2, "l2", NOW + timedelta(seconds=4))
    await _set_read_state(db, p_canonical, 1)
    await _set_read_state(db, p_loser, 2)
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    survivor_id = rows[0]["id"]
    read_state = (
        await db.execute(
            text("SELECT last_read_sequence FROM wagle_participant_read_states WHERE participant_id = :p"),
            {"p": survivor_id},
        )
    ).scalar_one()
    # 3 messages total, created_at order c1(seq1), l1(seq2), l2(seq3) after merge.
    # loser's own read-up-to-2nd-message (its own old sequence 2, i.e. l2) must
    # translate to new sequence 3, the actual highest read message -- not a
    # stale raw "2" (which would now point at l1, an unread regression).
    assert read_state == 3, read_state


async def test_case9_multiple_left_different_lifecycle_timestamps(db, board_singleton_index_dropped):
    family_id = await create_family(db, "Case9")
    membership_id = await create_bare_membership(db, family_id, "m1")
    canonical = await _make_room(db, family_id, NOW)
    loser1 = await _make_room(db, family_id, NOW + timedelta(seconds=1))
    loser2 = await _make_room(db, family_id, NOW + timedelta(seconds=2))
    await _add_participant(db, family_id, canonical, membership_id, status="left", joined_at=NOW - timedelta(days=10), left_at=NOW - timedelta(days=9))
    await _add_participant(db, family_id, loser1, membership_id, status="left", joined_at=NOW - timedelta(days=8), left_at=NOW - timedelta(days=7))
    await _add_participant(db, family_id, loser2, membership_id, status="left", joined_at=NOW - timedelta(days=6), left_at=NOW - timedelta(days=1))
    await db.commit()

    await _run_merge(db)

    rows = await _participants_for_membership(db, family_id, membership_id)
    assert len(rows) == 1, rows
    assert rows[0]["status"] == "left"
    assert rows[0]["joined_at"] == NOW - timedelta(days=10), "earliest joined_at preserved"
    assert rows[0]["left_at"] == NOW - timedelta(days=1), "latest left_at across the set preserved"


async def test_case10_different_family_same_membership_shape_is_isolated(db, board_singleton_index_dropped):
    """Cross-family isolation: an identical membership-id-shaped scenario in
    an unrelated Family (with a numerically colliding-looking but distinct
    membership row) must not affect this Family's own merge outcome."""
    family_a = await create_family(db, "Case10-A")
    family_b = await create_family(db, "Case10-B")
    membership_a = await create_bare_membership(db, family_a, "a1")
    membership_b = await create_bare_membership(db, family_b, "b1")

    canonical_a, loser_a = await _make_room(db, family_a, NOW), await _make_room(db, family_a, NOW + timedelta(seconds=1))
    await _add_participant(db, family_a, canonical_a, membership_a, status="left", joined_at=NOW - timedelta(days=2), left_at=NOW - timedelta(days=1))
    await _add_participant(db, family_a, loser_a, membership_a, status="active", joined_at=NOW)

    # Family B: single clean board, untouched negative control.
    room_b = await _make_room(db, family_b, NOW)
    p_b = await _add_participant(db, family_b, room_b, membership_b, status="active", joined_at=NOW)
    await _add_message(db, family_b, room_b, p_b, 1, "family b untouched", NOW)
    await db.commit()

    await _run_merge(db)

    rows_a = await _participants_for_membership(db, family_a, membership_a)
    assert len(rows_a) == 1 and rows_a[0]["status"] == "active"

    rows_b = await _participants_for_membership(db, family_b, membership_b)
    assert len(rows_b) == 1 and rows_b[0]["status"] == "active"
    assert rows_b[0]["room_id"] == room_b, "Family B's single room was never a merge target and must be unchanged"
    assert await _active_board_room_count(db, family_b) == 1
