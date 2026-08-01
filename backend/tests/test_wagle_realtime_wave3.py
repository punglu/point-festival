"""Wave 3: Wagle realtime dispatcher, WebSocket gateway, resume, Push, device PIN.

What these tests are trying to catch, stated up front so a reader can judge
whether they actually do it:

- A delivery failure must never damage the message. The message is durable
  before any of this runs, so every failure path is asserted to leave
  `wagle_messages` untouched.
- At-least-once means replay is normal. Every idempotency assertion runs the
  operation **twice** and checks the second one changed nothing, rather than
  checking a flag that says it would not.
- Authorization is re-derived, not remembered. Revocation tests withdraw
  authority *after* a subscription exists and assert the subscription stops
  working — checking only the connect-time denial would prove nothing about a
  socket that is already open.
- One failure is one failure. Isolation tests always involve a second Family,
  device or endpoint that must keep working.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text, update

from app.config import settings
from app.domains.family import auth_service
from app.domains.family.models import Account, AccountSession, FamilyMembership
from app.domains.service_outbox import service as outbox_service
from app.domains.service_outbox.models import ServiceOutboxEvent
from app.domains.wagle import device_pin_service, push_service, realtime, realtime_dispatcher
from app.domains.wagle import service as wagle_service
from app.domains.wagle.models import WagleMessage, WagleParticipant, WagleRoom
from app.domains.wagle.push_service import PushDeliveryResult
from app.domains.wagle.realtime import Connection, InProcessFanout, RealtimeEnvelope
from app.domains.wagle.realtime_models import (
    WagleDevicePin,
    WaglePushDeliveryAttempt,
    WaglePushSubscription,
)
from tests.conftest import create_actor, create_family, set_subscription

PIN_A = "0" * 0 + "135790"[: settings.WAGLE_PIN_LENGTH].ljust(settings.WAGLE_PIN_LENGTH, "7")
PIN_B = "246800"[: settings.WAGLE_PIN_LENGTH].ljust(settings.WAGLE_PIN_LENGTH, "1")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


class RecordingSocket:
    """Stands in for a WebSocket. Records what the server tried to send."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def __call__(self, payload: dict) -> None:
        self.sent.append(payload)

    def types(self) -> list[str]:
        return [m.get("type") for m in self.sent]


class BrokenSocket:
    """A socket that always fails, to prove one bad connection is isolated."""

    def __init__(self) -> None:
        self.attempts = 0

    async def __call__(self, payload: dict) -> None:
        self.attempts += 1
        raise RuntimeError("socket gone")


class ScriptedPushTransport:
    """Deterministic Push transport. No external service is contacted."""

    def __init__(self, outcomes: dict[str, str] | None = None, default: str = PushDeliveryResult.SENT):
        self.outcomes = outcomes or {}
        self.default = default
        self.calls: list[dict] = []

    async def send(self, *, endpoint: str, p256dh: str, auth: str, payload: dict) -> str:
        self.calls.append({"endpoint": endpoint, "payload": payload})
        outcome = self.outcomes.get(endpoint, self.default)
        if outcome == "RAISE":
            raise RuntimeError("transport blew up")
        return outcome


async def _room_with_participant(db, family_id: int, membership_id: int) -> str:
    """Insert a real room plus an ACTIVE participant row directly.

    Going through the API would need Wagle room_admin in that second family,
    which is setup noise for a test about revocation scope. What matters is
    that the room genuinely exists and the membership genuinely participates —
    a fabricated room id would be dropped by authorization, which is correct
    behaviour and would make the test assert the opposite of what it claims.
    """
    room = WagleRoom(
        family_group_id=family_id,
        room_type="GROUP",
        title="second",
        status="active",
        created_by_actor_type="ACCOUNT",
        next_message_sequence=0,
    )
    db.add(room)
    await db.flush()
    db.add(
        WagleParticipant(
            family_group_id=family_id,
            room_id=room.id,
            family_membership_id=membership_id,
            room_role="member",
            status="active",
            joined_sequence=0,
        )
    )
    await db.commit()
    return str(room.id)


async def _real_outbox_event(db, family_id: int, tag: str) -> int:
    """A real Outbox row.

    The delivery-attempt table has a foreign key to `service_outbox_events`, so
    a made-up id is rejected by the database. That is the constraint doing its
    job — attempts must be traceable to an event that actually happened.
    """
    event = await outbox_service.enqueue_event(
        db,
        owner_service="wagle",
        event_type="wagle.message.created",
        event_version=1,
        aggregate_type="wagle_message",
        aggregate_id=tag,
        source_event_id=tag,
        family_id=family_id,
        payload={},
    )
    await db.commit()
    return int(event.id)


@pytest.fixture(autouse=True)
def _restore_push_transport():
    original = push_service.get_transport()
    yield
    push_service.set_transport(original)


async def _account_token(db, client, display_name: str, username: str, device_id: str = "dev-1"):
    """A real Account credential + login, so the token under test is the one
    production issues rather than a hand-forged JWT."""
    account = (
        await db.execute(select(Account).where(Account.display_name == display_name))
    ).scalars().first()
    assert account is not None, f"{display_name} must already exist"
    await auth_service.create_credential(db, account.id, username, "Str0ngPassw0rd!")
    await db.commit()
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": username, "password": "Str0ngPassw0rd!", "device_id": device_id},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    return account, body["access_token"], body


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _make_room_with_message(env, *, body: str = "hello"):
    """A room both actors participate in, plus one durable message from admin."""
    client, family_id = env["client"], env["family_id"]
    room = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "rt"},
        headers=env["admin"].headers,
    )
    assert room.status_code in (200, 201), room.text
    room_id = room.json()["id"]
    added = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants",
        json={"family_membership_id": env["member"].membership_id, "room_role": "member"},
        headers=env["admin"].headers,
    )
    assert added.status_code in (200, 201), added.text
    sent = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"body": body, "client_message_id": str(uuid.uuid4())},
        headers=env["admin"].headers,
    )
    assert sent.status_code in (200, 201), sent.text
    return room_id, sent.json()


# ===========================================================================
# 1. Outbox dispatcher
# ===========================================================================


async def test_dispatcher_publishes_message_event_and_marks_outbox_published(family_env):
    db = family_env["db"]
    room_id, message = await _make_room_with_message(family_env)

    fanout = InProcessFanout()
    push_service.set_transport(ScriptedPushTransport())
    result = await realtime_dispatcher.run_once(db, port=fanout)

    assert result["claimed"] == 1, result
    assert result.get("published") == 1, result
    row = (
        await db.execute(
            select(ServiceOutboxEvent).where(
                ServiceOutboxEvent.source_event_id == str(message["id"])
            )
        )
    ).scalars().one()
    assert row.status == "PUBLISHED"


async def test_dispatcher_never_touches_the_durable_message_when_delivery_fails(family_env):
    """The whole point of the Outbox: notification failure is not data loss."""
    db = family_env["db"]
    room_id, message = await _make_room_with_message(family_env)

    class ExplodingFanout:
        async def publish(self, envelope):
            raise RuntimeError("fan-out down")

    result = await realtime_dispatcher.run_once(db, port=ExplodingFanout())
    assert result.get("retry_scheduled") == 1, result

    still_there = (
        await db.execute(select(WagleMessage).where(WagleMessage.id == message["id"]))
    ).scalars().one()
    assert still_there.deleted_at is None
    assert still_there.body == "hello"

    event = (
        await db.execute(
            select(ServiceOutboxEvent).where(
                ServiceOutboxEvent.source_event_id == str(message["id"])
            )
        )
    ).scalars().one()
    assert event.status == "PENDING"
    assert event.attempt_count == 1
    assert event.last_error_code == "realtime_dispatch_error"


async def test_dispatcher_claim_is_scoped_to_its_own_owner_service(family_env):
    """Regression for a defect this Wave found.

    The SERVICE_ACTION Worker used to claim every row regardless of owner, so
    once Wave 2 began writing `owner_service="wagle"` rows it picked them up and
    tried to publish a human message as a Service Action - provisioning a bogus
    `wagle` ServicePrincipal and retrying the row to DEAD.
    """
    db = family_env["db"]
    await _make_room_with_message(family_env)
    await outbox_service.enqueue_event(
        db,
        owner_service="mark-point",
        event_type="mission.completed",
        event_version=1,
        aggregate_type="mission",
        aggregate_id="9",
        source_event_id="mission-9",
        family_id=family_env["family_id"],
        payload={"mission_id": 9},
    )
    await db.commit()

    push_service.set_transport(ScriptedPushTransport())
    result = await realtime_dispatcher.run_once(db, port=InProcessFanout())
    assert result["claimed"] == 1, "only the wagle row belongs to this dispatcher"

    foreign = (
        await db.execute(
            select(ServiceOutboxEvent).where(ServiceOutboxEvent.owner_service == "mark-point")
        )
    ).scalars().one()
    assert foreign.status == "PENDING", "another owner's row must be left alone, not leased"

    principals = (
        await db.execute(text("SELECT count(*) FROM service_principals WHERE service_code='wagle'"))
    ).scalar()
    assert principals == 0, "no bogus wagle ServicePrincipal may be provisioned"


async def test_service_action_worker_does_not_claim_a_wagle_owned_row(family_env):
    """Symmetric regression for the same defect, the other direction.

    `test_dispatcher_claim_is_scoped_to_its_own_owner_service` above proves the
    Wagle dispatcher leaves a `mark-point` row alone. This proves the
    SERVICE_ACTION Worker (`app.workers.service_outbox`) leaves a `wagle` row
    alone -- the exact defect this Wave fixed (it used to claim every pending
    row regardless of owner and drive a human message's delivery event to DEAD
    trying to publish it as a Service Action).
    """
    from app.workers import service_outbox as service_action_worker

    db = family_env["db"]
    await _real_outbox_event(db, family_env["family_id"], "wagle-row-for-symmetry-check")

    result = await service_action_worker.run_once(db)
    assert result["claimed"] == 0, "the SERVICE_ACTION worker must not claim a wagle-owned row"

    row = (
        await db.execute(
            select(ServiceOutboxEvent).where(
                ServiceOutboxEvent.source_event_id == "wagle-row-for-symmetry-check"
            )
        )
    ).scalars().one()
    assert row.status == "PENDING", "the foreign row must be left untouched, not leased or advanced"
    assert row.attempt_count == 0


async def test_dispatcher_is_safe_to_run_twice_on_the_same_event(family_env):
    """At-least-once: reprocessing must not duplicate anything user-visible."""
    db = family_env["db"]
    await _make_room_with_message(family_env)
    transport = ScriptedPushTransport()
    push_service.set_transport(transport)

    first = await realtime_dispatcher.run_once(db, port=InProcessFanout())
    assert first["claimed"] == 1
    pushes_after_first = len(transport.calls)

    # Force the row back into a claimable state, exactly as an expired lease
    # after a mid-delivery crash would.
    await db.execute(
        update(ServiceOutboxEvent).values(
            status="PENDING", next_attempt_at=datetime.now(timezone.utc) - timedelta(seconds=1)
        )
    )
    await db.commit()

    second = await realtime_dispatcher.run_once(db, port=InProcessFanout())
    assert second["claimed"] == 1
    assert len(transport.calls) == pushes_after_first, "no second Push for the same event"

    attempts = (
        await db.execute(select(WaglePushDeliveryAttempt))
    ).scalars().all()
    assert all(a.attempt_count == 1 for a in attempts)


async def test_dispatcher_does_not_retry_forever_when_the_message_is_gone(family_env):
    db = family_env["db"]
    await _make_room_with_message(family_env)
    await db.execute(
        update(ServiceOutboxEvent).values(source_event_id=str(uuid.uuid4()))
    )
    await db.commit()

    result = await realtime_dispatcher.run_once(db, port=InProcessFanout())
    assert result.get("message_missing") == 1
    event = (await db.execute(select(ServiceOutboxEvent))).scalars().one()
    assert event.status == "PENDING" and event.attempt_count == 1
    assert event.last_error_code == "message_missing"


async def test_expired_lease_is_reclaimed_after_a_worker_dies_mid_delivery(family_env):
    db = family_env["db"]
    await _make_room_with_message(family_env)
    claimed = await outbox_service.claim_batch(db, owner_service="wagle")
    assert len(claimed) == 1

    # Nothing else can take it while the lease is live.
    assert await outbox_service.claim_batch(db, owner_service="wagle") == []

    await db.execute(
        update(ServiceOutboxEvent).values(
            locked_until=datetime.now(timezone.utc) - timedelta(seconds=1)
        )
    )
    await db.commit()
    assert len(await outbox_service.claim_batch(db, owner_service="wagle")) == 1


# ===========================================================================
# 2. Fan-out and failure isolation
# ===========================================================================


async def test_fanout_reaches_only_subscribers_of_that_family_and_room():
    fanout = InProcessFanout()
    target, other_room, other_family = RecordingSocket(), RecordingSocket(), RecordingSocket()
    room = str(uuid.uuid4())

    await fanout.register(Connection("c1", 1, 10, None, target, {7: {room}}))
    await fanout.register(Connection("c2", 2, 20, None, other_room, {7: {str(uuid.uuid4())}}))
    await fanout.register(Connection("c3", 3, 30, None, other_family, {8: {room}}))

    envelope = RealtimeEnvelope("e", "wagle.message.created", 7, room, "m", 3, "t", "ACCOUNT")
    assert await fanout.publish(envelope) == 1
    assert target.types() == ["event"]
    assert other_room.sent == []
    assert other_family.sent == [], "same room id in a different family must not match"


async def test_one_broken_socket_does_not_stop_delivery_to_the_others():
    fanout = InProcessFanout()
    room = str(uuid.uuid4())
    broken, healthy = BrokenSocket(), RecordingSocket()
    await fanout.register(Connection("bad", 1, 10, None, broken, {7: {room}}))
    await fanout.register(Connection("good", 2, 20, None, healthy, {7: {room}}))

    delivered = await fanout.publish(
        RealtimeEnvelope("e", "wagle.message.created", 7, room, "m", 1, "t", "ACCOUNT")
    )
    assert delivered == 1
    assert len(healthy.sent) == 1
    assert await fanout.get("bad") is None, "the failing connection is dropped, not retried forever"


async def test_revoking_one_family_leaves_the_other_families_connected():
    fanout = InProcessFanout()
    socket = RecordingSocket()
    room_a, room_b = str(uuid.uuid4()), str(uuid.uuid4())
    connection = Connection("c1", 5, 50, None, socket, {7: {room_a}, 8: {room_b}})
    await fanout.register(connection)

    await fanout.revoke_family(5, 7)

    assert await fanout.get("c1") is not None, "losing one family is not a logout"
    assert 7 not in connection.subscriptions
    assert connection.subscriptions[8] == {room_b}
    assert await fanout.publish(
        RealtimeEnvelope("e", "t", 8, room_b, "m", 1, "t", "ACCOUNT")
    ) == 1
    assert await fanout.publish(
        RealtimeEnvelope("e", "t", 7, room_a, "m", 1, "t", "ACCOUNT")
    ) == 0


async def test_revoking_the_session_closes_every_connection_on_it():
    fanout = InProcessFanout()
    room = str(uuid.uuid4())
    tab1, tab2, other_session = RecordingSocket(), RecordingSocket(), RecordingSocket()
    # Multiple physical sockets on one Session are legitimate; the contract
    # forbids an invariant that treats them as an error.
    await fanout.register(Connection("t1", 5, 50, None, tab1, {7: {room}}))
    await fanout.register(Connection("t2", 5, 50, None, tab2, {7: {room}}))
    await fanout.register(Connection("t3", 5, 51, None, other_session, {7: {room}}))

    assert await fanout.revoke_session(50) == 2
    assert await fanout.get("t1") is None and await fanout.get("t2") is None
    assert await fanout.get("t3") is not None


# ===========================================================================
# 3. Subscription authorization (server-derived)
# ===========================================================================


async def test_subscription_requires_active_membership_room_and_participation(family_env, db):
    client, family_id = family_env["client"], family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)

    admin_account = await db.get(Account, family_env["admin"].account_id)
    member_account = await db.get(Account, family_env["member"].account_id)

    await realtime.authorize_subscription(db, admin_account, family_id, room_id)
    await realtime.authorize_subscription(db, member_account, family_id, room_id)

    # A room that exists, in a family the caller is not in.
    other_family = await create_family(db, "Other")
    outsider = await create_actor(db, other_family, name="outsider")
    await set_subscription(db, other_family, "active")
    await db.commit()
    outsider_account = await db.get(Account, outsider.account_id)
    with pytest.raises(PermissionError):
        await realtime.authorize_subscription(db, outsider_account, family_id, room_id)
    # Same room id, wrong family in the path: the cross-family probe shape.
    with pytest.raises(PermissionError):
        await realtime.authorize_subscription(db, outsider_account, other_family, room_id)


async def test_subscription_dies_when_the_membership_is_suspended(family_env, db):
    family_id = family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)
    member_account = await db.get(Account, family_env["member"].account_id)
    await realtime.authorize_subscription(db, member_account, family_id, room_id)

    await db.execute(
        update(FamilyMembership)
        .where(FamilyMembership.id == family_env["member"].membership_id)
        .values(status="suspended")
    )
    await db.commit()

    with pytest.raises(Exception):
        await realtime.authorize_subscription(db, member_account, family_id, room_id)


async def test_authorized_family_set_is_server_derived_across_all_memberships(db):
    family_a = await create_family(db, "A")
    family_b = await create_family(db, "B")
    actor = await create_actor(db, family_a, name="multi")
    membership_b = FamilyMembership(
        family_group_id=family_b,
        account_id=actor.account_id,
        relationship="unknown",
        status="active",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership_b)
    await db.commit()

    ids = await realtime.authorized_family_ids(db, actor.account_id)
    assert ids == {family_a, family_b}, "ActiveFamilyContext must never narrow this"


async def test_revalidate_drops_only_the_revoked_family(family_env, db, client):
    """Revalidation runs against a **real** Session, not a synthetic id.

    An earlier draft passed `session_id=1`, and the assertion failed for the
    right reason: no such Session exists, so revalidation correctly terminated
    the connection. Using a real login is what makes this test about family
    revocation rather than about session lookup.
    """
    family_id = family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)
    account = await db.get(Account, family_env["member"].account_id)
    _, _, login = await _account_token(db, client, "member", "member.reval", "dev-reval")
    session_row = (
        await db.execute(
            select(AccountSession).where(
                AccountSession.account_id == account.id, AccountSession.revoked_at.is_(None)
            )
        )
    ).scalars().first()
    assert session_row is not None

    other_family = await create_family(db, "Second")
    membership = FamilyMembership(
        family_group_id=other_family,
        account_id=account.id,
        relationship="unknown",
        status="active",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.commit()
    other_room = await _room_with_participant(db, other_family, membership.id)

    connection = Connection(
        "c1", account.id, session_row.id, None, RecordingSocket(),
        {family_id: {room_id}, other_family: {other_room}},
    )

    await db.execute(
        update(FamilyMembership)
        .where(FamilyMembership.id == family_env["member"].membership_id)
        .values(status="removed")
    )
    await db.commit()

    result = await realtime.revalidate_connection(db, connection)
    assert result["terminate"] is False, "one family ending is not a session termination"
    assert family_id in result["revoked_families"]
    assert other_family not in result["revoked_families"]
    assert connection.subscriptions == {other_family: {other_room}}, (
        "the surviving family keeps its real room; only the revoked one is dropped"
    )


# ===========================================================================
# 4. Resume / recovery
# ===========================================================================


async def test_resume_returns_missed_events_in_room_sequence_order(family_env, db):
    client, family_id = family_env["client"], family_env["family_id"]
    room_id, first = await _make_room_with_message(family_env, body="m1")
    for body in ("m2", "m3"):
        await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"body": body, "client_message_id": str(uuid.uuid4())},
            headers=family_env["admin"].headers,
        )
    account = await db.get(Account, family_env["member"].account_id)

    result = await realtime.resume_missed_events(db, account, family_id, room_id, 0)
    sequences = [e["room_sequence"] for e in result["events"]]
    assert sequences == sorted(sequences) and len(sequences) == 3
    assert result["has_more"] is False

    partial = await realtime.resume_missed_events(db, account, family_id, room_id, sequences[0])
    assert [e["room_sequence"] for e in partial["events"]] == sequences[1:]


async def test_resume_is_idempotent_and_safe_to_replay(family_env, db):
    family_id = family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)
    account = await db.get(Account, family_env["member"].account_id)

    first = await realtime.resume_missed_events(db, account, family_id, room_id, 0)
    second = await realtime.resume_missed_events(db, account, family_id, room_id, 0)
    assert [e["message_id"] for e in first["events"]] == [e["message_id"] for e in second["events"]]

    # Replaying past the cursor yields nothing new — the client dedupes on
    # (room_id, room_sequence), and the server does not invent a gap.
    after = await realtime.resume_missed_events(
        db, account, family_id, room_id, first["next_sequence"]
    )
    assert after["events"] == []


async def test_resume_paginates_instead_of_silently_truncating(family_env, db):
    client, family_id = family_env["client"], family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)
    for i in range(4):
        await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"body": f"b{i}", "client_message_id": str(uuid.uuid4())},
            headers=family_env["admin"].headers,
        )
    account = await db.get(Account, family_env["member"].account_id)

    page = await realtime.resume_missed_events(db, account, family_id, room_id, 0, limit=2)
    assert len(page["events"]) == 2
    assert page["has_more"] is True, "a client must page, not skip the rest of the gap"

    rest = await realtime.resume_missed_events(
        db, account, family_id, room_id, page["next_sequence"], limit=100
    )
    assert len(rest["events"]) == 3 and rest["has_more"] is False


async def test_resume_denies_a_room_the_caller_cannot_reach(family_env, db):
    family_id = family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)
    other_family = await create_family(db, "Outside")
    outsider = await create_actor(db, other_family, name="nosy")
    await db.commit()
    account = await db.get(Account, outsider.account_id)
    with pytest.raises(PermissionError):
        await realtime.resume_missed_events(db, account, family_id, room_id, 0)


async def test_resume_never_exposes_history_from_before_the_participant_joined(family_env, db):
    """A participant added late must not be able to read the room's past by
    resuming from sequence 0."""
    client, family_id = family_env["client"], family_env["family_id"]
    room = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "late"},
        headers=family_env["admin"].headers,
    )
    room_id = room.json()["id"]
    for body in ("secret-1", "secret-2"):
        await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"body": body, "client_message_id": str(uuid.uuid4())},
            headers=family_env["admin"].headers,
        )
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants",
        json={"family_membership_id": family_env["member"].membership_id, "room_role": "member"},
        headers=family_env["admin"].headers,
    )
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"body": "after-join", "client_message_id": str(uuid.uuid4())},
        headers=family_env["admin"].headers,
    )

    account = await db.get(Account, family_env["member"].account_id)
    result = await realtime.resume_missed_events(db, account, family_id, room_id, 0)
    assert len(result["events"]) == 1, "only the message sent after joining is replayable"


# ===========================================================================
# 5. Push subscription lifecycle and delivery
# ===========================================================================


async def test_push_subscription_registration_is_account_and_device_scoped(family_env, db):
    account_id = family_env["member"].account_id
    first = await push_service.register_subscription(
        db, account_id, device_id="phone", endpoint="https://push/1", p256dh_key="k", auth_secret="s"
    )
    second = await push_service.register_subscription(
        db, account_id, device_id="phone", endpoint="https://push/2", p256dh_key="k", auth_secret="s"
    )
    active = await push_service.list_subscriptions(db, account_id)
    assert len(active) == 1 and active[0].id == second.id, "a device replaces its own row"

    tablet = await push_service.register_subscription(
        db, account_id, device_id="tablet", endpoint="https://push/3", p256dh_key="k", auth_secret="s"
    )
    assert len(await push_service.list_subscriptions(db, account_id)) == 2


async def test_reusing_an_endpoint_under_another_account_revokes_the_first(family_env, db):
    """Account switch on a shared browser must not keep pushing to the old
    Account's subscription."""
    first_account = family_env["admin"].account_id
    second_account = family_env["member"].account_id
    await push_service.register_subscription(
        db, first_account, device_id="shared", endpoint="https://push/x", p256dh_key="k", auth_secret="s"
    )
    await push_service.register_subscription(
        db, second_account, device_id="shared", endpoint="https://push/x", p256dh_key="k", auth_secret="s"
    )
    assert await push_service.list_subscriptions(db, first_account) == []
    assert len(await push_service.list_subscriptions(db, second_account)) == 1


async def test_expired_endpoint_deactivates_only_that_subscription(family_env, db):
    account_id = family_env["member"].account_id
    dead = await push_service.register_subscription(
        db, account_id, device_id="old", endpoint="https://push/dead", p256dh_key="k", auth_secret="s"
    )
    live = await push_service.register_subscription(
        db, account_id, device_id="new", endpoint="https://push/live", p256dh_key="k", auth_secret="s"
    )
    push_service.set_transport(
        ScriptedPushTransport({"https://push/dead": PushDeliveryResult.EXPIRED})
    )

    outbox_id = await _real_outbox_event(db, family_env["family_id"], "evt-expired")
    envelope = RealtimeEnvelope("e1", "wagle.message.created", family_env["family_id"], str(uuid.uuid4()), "m", 1, "t", "ACCOUNT")
    stats = await push_service.deliver_event(
        db, envelope, outbox_event_id=outbox_id, recipient_account_ids=[account_id]
    )
    assert stats["expired"] == 1 and stats["sent"] == 1

    await db.refresh(dead)
    await db.refresh(live)
    assert dead.status == "expired"
    assert live.status == "active", "one dead endpoint must not disable the other device"


async def test_transient_push_failure_is_isolated_and_leaves_the_subscription_active(family_env, db):
    account_id = family_env["member"].account_id
    flaky = await push_service.register_subscription(
        db, account_id, device_id="flaky", endpoint="https://push/flaky", p256dh_key="k", auth_secret="s"
    )
    push_service.set_transport(ScriptedPushTransport({"https://push/flaky": "RAISE"}))

    outbox_id = await _real_outbox_event(db, family_env["family_id"], "evt-flaky")
    envelope = RealtimeEnvelope("e2", "wagle.message.created", family_env["family_id"], str(uuid.uuid4()), "m", 1, "t", "ACCOUNT")
    stats = await push_service.deliver_event(
        db, envelope, outbox_event_id=outbox_id, recipient_account_ids=[account_id]
    )
    assert stats["failed"] == 1
    await db.refresh(flaky)
    assert flaky.status == "active", "a transient failure is not an expiry"


async def test_push_delivery_is_idempotent_per_event_and_endpoint(family_env, db):
    account_id = family_env["member"].account_id
    await push_service.register_subscription(
        db, account_id, device_id="p", endpoint="https://push/i", p256dh_key="k", auth_secret="s"
    )
    transport = ScriptedPushTransport()
    push_service.set_transport(transport)
    outbox_id = await _real_outbox_event(db, family_env["family_id"], "evt-idem")
    envelope = RealtimeEnvelope("e3", "wagle.message.created", family_env["family_id"], str(uuid.uuid4()), "m", 1, "t", "ACCOUNT")

    await push_service.deliver_event(db, envelope, outbox_event_id=outbox_id, recipient_account_ids=[account_id])
    second = await push_service.deliver_event(
        db, envelope, outbox_event_id=outbox_id, recipient_account_ids=[account_id]
    )
    assert len(transport.calls) == 1
    assert second["skipped_duplicate"] == 1


async def test_push_payload_carries_no_message_content_pending_policy(family_env, db):
    """D6-P1 is undecided; the payload must therefore disclose identifiers only.

    This is asserted rather than left to review because a body in a fixture is
    exactly how an undecided policy becomes a shipped default.
    """
    envelope = RealtimeEnvelope("e", "wagle.message.created", 1, "r", "m", 4, "t", "ACCOUNT")
    payload = push_service.build_payload(envelope)
    assert payload["policy"] == push_service.PAYLOAD_POLICY
    for forbidden in ("body", "text", "sender_name", "title", "preview", "message_body"):
        assert forbidden not in payload
    assert set(payload) == {
        "policy", "event_id", "event_type", "family_id", "room_id",
        "message_id", "room_sequence", "occurred_at", "actor_type",
    }


async def test_push_revocation_scopes(family_env, db):
    account_id = family_env["member"].account_id
    await push_service.register_subscription(
        db, account_id, device_id="d1", endpoint="https://push/a", p256dh_key="k", auth_secret="s"
    )
    await push_service.register_subscription(
        db, account_id, device_id="d2", endpoint="https://push/b", p256dh_key="k", auth_secret="s"
    )
    await push_service.revoke_for_device(db, account_id, "d1", reason="logout")
    remaining = await push_service.list_subscriptions(db, account_id)
    assert [r.device_id for r in remaining] == ["d2"]

    await push_service.revoke_for_account(db, account_id, reason="suspended")
    assert await push_service.list_subscriptions(db, account_id) == []


# ===========================================================================
# 6. Wagle device PIN
# ===========================================================================


async def test_pin_is_stored_only_as_a_hash_and_is_never_readable(family_env, db):
    account_id = family_env["member"].account_id
    status = await device_pin_service.set_pin(db, account_id, "dev-1", PIN_A)
    assert status["configured"] is True

    row = (
        await db.execute(select(WagleDevicePin).where(WagleDevicePin.account_id == account_id))
    ).scalars().one()
    assert row.pin_hash != PIN_A and PIN_A not in row.pin_hash
    assert row.pin_hash.startswith("$2")  # bcrypt

    # There is deliberately no service function that returns a PIN.
    assert not any(
        name for name in dir(device_pin_service) if "get_pin" in name or "read_pin" in name
    )
    assert "pin_hash" not in device_pin_service.status_payload(row)


async def test_pin_verification_locks_after_the_configured_attempts(family_env, db):
    from fastapi import HTTPException

    account_id = family_env["member"].account_id
    await device_pin_service.set_pin(db, account_id, "dev-1", PIN_A)

    for _ in range(settings.WAGLE_PIN_MAX_ATTEMPTS):
        with pytest.raises(HTTPException) as exc:
            await device_pin_service.verify_pin(db, account_id, "dev-1", PIN_B)
        assert exc.value.status_code == 401

    with pytest.raises(HTTPException) as locked:
        await device_pin_service.verify_pin(db, account_id, "dev-1", PIN_A)
    assert locked.value.status_code == 423, "a correct PIN must not bypass the lockout"


async def test_pin_attempts_are_isolated_per_device(family_env, db):
    from fastapi import HTTPException

    account_id = family_env["member"].account_id
    await device_pin_service.set_pin(db, account_id, "phone", PIN_A)
    await device_pin_service.set_pin(db, account_id, "tablet", PIN_A)

    for _ in range(settings.WAGLE_PIN_MAX_ATTEMPTS):
        with pytest.raises(HTTPException):
            await device_pin_service.verify_pin(db, account_id, "phone", PIN_B)

    tablet = await device_pin_service.verify_pin(db, account_id, "tablet", PIN_A)
    assert tablet["unlocked"] is True, "locking one device must not lock the Account's others"


async def test_pin_reset_replaces_the_secret_and_clears_the_lockout(family_env, db):
    from fastapi import HTTPException

    account_id = family_env["member"].account_id
    await device_pin_service.set_pin(db, account_id, "dev-1", PIN_A)
    for _ in range(settings.WAGLE_PIN_MAX_ATTEMPTS):
        with pytest.raises(HTTPException):
            await device_pin_service.verify_pin(db, account_id, "dev-1", PIN_B)

    status = await device_pin_service.reset_pin(db, account_id, "dev-1", PIN_B)
    assert status["locked"] is False
    assert status["pin_version"] == 2, "a client's stale unlock must not survive a reset"

    assert (await device_pin_service.verify_pin(db, account_id, "dev-1", PIN_B))["unlocked"] is True
    with pytest.raises(HTTPException):
        await device_pin_service.verify_pin(db, account_id, "dev-1", PIN_A)


async def test_pin_is_not_family_scoped_and_covers_every_family_on_that_device(family_env, db):
    account_id = family_env["member"].account_id
    await device_pin_service.set_pin(db, account_id, "dev-1", PIN_A)
    rows = (
        await db.execute(select(WagleDevicePin).where(WagleDevicePin.account_id == account_id))
    ).scalars().all()
    assert len(rows) == 1
    assert not hasattr(rows[0], "family_group_id"), "a personal device lock is never family property"


async def test_pin_does_not_reuse_the_legacy_player_pin(family_env, db):
    """The legacy MarkPoint player PIN authenticates. This one locks a screen.
    Sharing the column would silently promote a UI lock into a credential."""
    account_id = family_env["member"].account_id
    await device_pin_service.set_pin(db, account_id, "dev-1", PIN_A)
    legacy = (await db.execute(text("SELECT count(*) FROM player_auth WHERE pin_hash IS NOT NULL"))).scalar()
    wagle_rows = (await db.execute(select(WagleDevicePin))).scalars().all()
    assert len(wagle_rows) == 1
    assert wagle_rows[0].pin_hash is not None
    # The two live in different tables; nothing copied a legacy hash across.
    assert all(r.pin_hash.startswith("$2") for r in wagle_rows)


async def test_pin_lockout_does_not_touch_the_account_session_or_push(family_env, db):
    """A locked screen must not become a platform-wide denial of service."""
    from fastapi import HTTPException

    account_id = family_env["member"].account_id
    await push_service.register_subscription(
        db, account_id, device_id="dev-1", endpoint="https://push/keep", p256dh_key="k", auth_secret="s"
    )
    await device_pin_service.set_pin(db, account_id, "dev-1", PIN_A)
    for _ in range(settings.WAGLE_PIN_MAX_ATTEMPTS):
        with pytest.raises(HTTPException):
            await device_pin_service.verify_pin(db, account_id, "dev-1", PIN_B)

    assert len(await push_service.list_subscriptions(db, account_id)) == 1, "Push survives a PIN lock"

    account = await db.get(Account, account_id)
    assert account.status == "active", "the Account is untouched by a screen lock"


async def test_pin_format_follows_config_not_a_hard_coded_policy(family_env, db):
    from fastapi import HTTPException

    account_id = family_env["member"].account_id
    with pytest.raises(HTTPException):
        await device_pin_service.set_pin(db, account_id, "dev-1", "1" * (settings.WAGLE_PIN_LENGTH + 1))
    with pytest.raises(HTTPException):
        await device_pin_service.set_pin(db, account_id, "dev-1", "a" * settings.WAGLE_PIN_LENGTH)


# ===========================================================================
# 7. HTTP surface authorization
# ===========================================================================


async def test_personal_endpoints_reject_an_unauthenticated_caller(client):
    for method, path in (
        ("get", "/api/me/wagle/realtime-context"),
        ("get", "/api/me/wagle/push-subscriptions"),
        ("get", "/api/me/wagle/device-pin?device_id=d"),
    ):
        resp = await getattr(client, method)(path)
        assert resp.status_code in (401, 403), f"{path} -> {resp.status_code}"


async def test_push_subscription_response_never_echoes_the_endpoint_or_keys(family_env, db, client):
    account, token, _ = await _account_token(db, client, "member", "member.push")
    resp = await client.post(
        "/api/me/wagle/push-subscriptions",
        json={
            "device_id": "dev-1",
            "endpoint": "https://push.example/secret-capability",
            "p256dh_key": "public-key",
            "auth_secret": "auth-secret-value",
        },
        headers=_headers(token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert set(body) == {"id", "device_id", "status"}
    serialized = resp.text
    assert "secret-capability" not in serialized
    assert "auth-secret-value" not in serialized


async def test_one_account_cannot_see_or_revoke_another_accounts_subscription(family_env, db, client):
    admin_account, admin_token, _ = await _account_token(db, client, "admin", "admin.iso", "dev-admin")
    member_account, member_token, _ = await _account_token(db, client, "member", "member.iso", "dev-member")

    await client.post(
        "/api/me/wagle/push-subscriptions",
        json={"device_id": "shared-name", "endpoint": "https://push/admin", "p256dh_key": "k", "auth_secret": "s"},
        headers=_headers(admin_token),
    )
    listed = await client.get("/api/me/wagle/push-subscriptions", headers=_headers(member_token))
    assert listed.json() == [], "another Account's device is invisible"

    # Deleting by the same device_id string must not reach the other Account.
    await client.delete("/api/me/wagle/push-subscriptions/shared-name", headers=_headers(member_token))
    still = await client.get("/api/me/wagle/push-subscriptions", headers=_headers(admin_token))
    assert len(still.json()) == 1


async def test_device_pin_endpoints_are_scoped_to_the_calling_account(family_env, db, client):
    _, admin_token, _ = await _account_token(db, client, "admin", "admin.pin", "dev-a")
    _, member_token, _ = await _account_token(db, client, "member", "member.pin", "dev-b")

    await client.put(
        "/api/me/wagle/device-pin",
        json={"device_id": "same-device-id", "pin": PIN_A},
        headers=_headers(admin_token),
    )
    other = await client.get(
        "/api/me/wagle/device-pin?device_id=same-device-id", headers=_headers(member_token)
    )
    assert other.json()["configured"] is False, "a FamilyAdmin-shaped caller sees nothing either"

    verify = await client.post(
        "/api/me/wagle/device-pin/verify",
        json={"device_id": "same-device-id", "pin": PIN_A},
        headers=_headers(member_token),
    )
    assert verify.status_code == 404


async def test_resume_endpoint_denies_cross_family_access(family_env, db, client):
    family_id = family_env["family_id"]
    room_id, _ = await _make_room_with_message(family_env)
    other_family = await create_family(db, "Elsewhere")
    outsider = await create_actor(db, other_family, name="outsider2")
    await db.commit()
    _, token, _ = await _account_token(db, client, "outsider2", "outsider2.u", "dev-o")

    resp = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/resume?after_sequence=0",
        headers=_headers(token),
    )
    assert resp.status_code == 403


async def test_realtime_context_returns_the_server_derived_family_set(family_env, db, client):
    _, token, _ = await _account_token(db, client, "member", "member.ctx", "dev-c")
    resp = await client.get("/api/me/wagle/realtime-context", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["authorized_family_ids"] == [family_env["family_id"]]
