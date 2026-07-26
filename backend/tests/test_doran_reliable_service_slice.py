"""PHASE2-DORAN-R2B2-RELIABLE-SERVICE-SLICE-001 real-PostgreSQL suite.

Covers the 28 required items from the R2-B2 handoff: generic Transactional
Outbox (1-10), SERVICE Room self-onboarding (11-17), ingress security/limits
(18-22), and a full Mark Point -> Outbox -> Worker -> Doran -> user-visible
message E2E chain (23-28).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import bcrypt
import pytest
from sqlalchemy import text

from app.domains.doran import service as doran_service
from app.domains.mission import service as mission_service
from app.domains.mission.models import Mission
from app.domains.service_outbox import service as outbox_service
from app.workers import service_outbox as worker
from tests.conftest import AsyncSessionLocal, create_actor, create_family, run_concurrent, set_subscription


async def _complete_mission(db, player_id: int, *, point: int = 100, text_: str = "설거지") -> Mission:
    mission = Mission(player_id=player_id, date=date.today(), text=text_, point=point, status="active")
    db.add(mission)
    await db.flush()
    await mission_service.update_mission_status(db, mission.id, "completed", role="admin")
    await db.refresh(mission)
    return mission


async def _outbox_rows(db, family_id: int | None = None) -> list:
    stmt = text(
        "SELECT id, owner_service, event_type, family_id, status, attempt_count, payload, source_event_id "
        "FROM service_outbox_events" + (" WHERE family_id = :fid" if family_id is not None else "") + " ORDER BY id"
    )
    params = {"fid": family_id} if family_id is not None else {}
    return list((await db.execute(stmt, params)).mappings().all())


async def _concurrent(coroutines):
    """Run each business operation in its own real PostgreSQL session."""
    return await run_concurrent(coroutines)


async def _complete_in_own_session(mission_id: int):
    async with AsyncSessionLocal() as session:
        try:
            result = await mission_service.update_mission_status(session, mission_id, "completed", role="admin")
            return ("completed", result.status)
        except Exception as exc:
            await session.rollback()
            return ("rejected", getattr(exc, "status_code", type(exc).__name__))


# ---------------------------------------------------------------------------
# Outbox 1-10
# ---------------------------------------------------------------------------

async def test_outbox_00_same_mission_eight_concurrent_completions_are_serialized(family_env):
    """A Mission lock must allow one completion and reject stale followers.

    This is deliberately separate sessions over real PostgreSQL: a shared
    AsyncSession would not exercise row-lock serialization.
    """
    db, member, family_id = family_env["db"], family_env["member"], family_env["family_id"]
    mission = Mission(player_id=member.player_id, date=date.today(), text="eight-complete", point=41, status="active")
    db.add(mission)
    await db.commit()

    results = await _concurrent([lambda: _complete_in_own_session(mission.id) for _ in range(8)])
    assert [result[0] for result in results].count("completed") == 1, results
    assert [result[1] for result in results if result[0] == "rejected"] == [400] * 7

    row = (
        await db.execute(
            text(
                "SELECT m.status, dp.earned, p.total_earned, "
                "(SELECT count(*) FROM service_outbox_events WHERE aggregate_id = m.id::text) "
                "FROM missions m JOIN players p ON p.id = m.player_id "
                "JOIN daily_points dp ON dp.player_id = m.player_id AND dp.date = m.date WHERE m.id = :id"
            ),
            {"id": mission.id},
        )
    ).one()
    assert row == ("completed", 41, 41, 1)

    delivered = await worker.run_once(db)
    assert delivered["published"] == 1
    message_count = (
        await db.execute(
            text(
                "SELECT count(*) FROM doran_messages dm JOIN service_outbox_events o "
                "ON o.source_event_id = dm.source_event_id WHERE o.aggregate_id = :id"
            ),
            {"id": str(mission.id)},
        )
    ).scalar_one()
    assert message_count == 1


async def test_outbox_00_same_mission_eight_concurrent_reverts_are_serialized(family_env):
    db, member = family_env["db"], family_env["member"]
    mission = await _complete_mission(db, member.player_id, point=43, text_="eight-revert")

    async def revert_in_own_session():
        async with AsyncSessionLocal() as session:
            try:
                result = await mission_service.admin_revert_mission(session, mission.id)
                await session.commit()
                return ("reverted", result.status)
            except Exception as exc:
                await session.rollback()
                return ("rejected", getattr(exc, "status_code", type(exc).__name__))

    results = await _concurrent([revert_in_own_session for _ in range(8)])
    assert [result[0] for result in results].count("reverted") == 1, results
    assert [result[1] for result in results if result[0] == "rejected"] == [404] * 7
    row = (
        await db.execute(
            text(
                "SELECT m.status, dp.earned, p.total_earned FROM missions m "
                "JOIN players p ON p.id = m.player_id JOIN daily_points dp "
                "ON dp.player_id = m.player_id AND dp.date = m.date WHERE m.id = :id"
            ),
            {"id": mission.id},
        )
    ).one()
    assert row == ("active", 0, 0)


async def test_outbox_00_concurrent_bulk_approval_counts_locked_pending_rows_once(family_env):
    db, member = family_env["db"], family_env["member"]
    points = [7, 11, 13]
    for point in points:
        db.add(Mission(player_id=member.player_id, date=date.today(), text=f"bulk-{point}", point=point, status="pending_approval"))
    await db.commit()

    async def approve_in_own_session():
        async with AsyncSessionLocal() as session:
            count = await mission_service.bulk_approve_missions(session, member.player_id, str(date.today()))
            await session.commit()
            return count

    results = await _concurrent([approve_in_own_session, approve_in_own_session])
    assert sorted(results) == [0, 3]
    total = (await db.execute(text("SELECT total_earned FROM players WHERE id = :id"), {"id": member.player_id})).scalar_one()
    completed = (await db.execute(text("SELECT count(*) FROM missions WHERE player_id = :id AND status = 'completed'"), {"id": member.player_id})).scalar_one()
    outbox = (await db.execute(text("SELECT count(*) FROM service_outbox_events"))).scalar_one()
    assert (total, completed, outbox) == (sum(points), 3, 0)


async def test_outbox_00_recompletion_has_two_distinct_occurrence_events(family_env):
    db, member, family_id = family_env["db"], family_env["member"], family_env["family_id"]
    mission = Mission(player_id=member.player_id, date=date.today(), text="recomplete", point=29, status="active")
    db.add(mission)
    await db.commit()
    await mission_service.update_mission_status(db, mission.id, "completed", role="admin")
    await mission_service.admin_revert_mission(db, mission.id)
    await db.commit()
    await mission_service.update_mission_status(db, mission.id, "completed", role="admin")

    rows = await _outbox_rows(db, family_id)
    assert len(rows) == 2
    assert len({row["source_event_id"] for row in rows}) == 2
    assert (await db.execute(text("SELECT total_earned FROM players WHERE id = :id"), {"id": member.player_id})).scalar_one() == 29
    delivered = await worker.run_once(db)
    assert delivered["published"] == 2
    assert (await db.execute(text("SELECT count(*) FROM doran_messages WHERE family_group_id = :id"), {"id": family_id})).scalar_one() == 2

async def test_outbox_01_business_success_creates_one_row(family_env):
    db, member = family_env["db"], family_env["member"]
    await _complete_mission(db, member.player_id)
    rows = await _outbox_rows(db, family_env["family_id"])
    assert len(rows) == 1
    assert rows[0]["owner_service"] == "mark-point"
    assert rows[0]["event_type"] == "mission.completed"
    assert rows[0]["status"] == "PENDING"
    assert rows[0]["payload"]["awarded_points"] == 100


async def test_outbox_02_rollback_creates_no_row(family_env):
    db, member = family_env["db"], family_env["member"]
    mission = Mission(player_id=member.player_id, date=date.today(), text="rollback-probe", point=50, status="completed")
    db.add(mission)
    await db.flush()
    await mission_service._emit_mission_completed_event(db, mission)
    assert len(await _outbox_rows(db, family_env["family_id"])) == 1
    await db.rollback()
    assert len(await _outbox_rows(db, family_env["family_id"])) == 0


async def test_outbox_03_retry_no_duplicate(family_env):
    db, family_id = family_env["db"], family_env["family_id"]
    kwargs = dict(
        owner_service="mark-point", event_type="mission.completed", event_version=1,
        aggregate_type="mission", aggregate_id="42", source_event_id="retry-probe-1",
        family_id=family_id, payload={"mission_id": 42},
    )
    first = await outbox_service.enqueue_event(db, **kwargs)
    await db.commit()
    second = await outbox_service.enqueue_event(db, **kwargs)
    await db.commit()
    assert first.id == second.id
    rows = await _outbox_rows(db, family_id)
    assert len(rows) == 1


async def test_outbox_04_worker_publishes_marks_published(family_env):
    db, member, family_id = family_env["db"], family_env["member"], family_env["family_id"]
    # family_env already has an active Doran subscription.
    await _complete_mission(db, member.player_id)
    result = await worker.run_once(db)
    assert result["published"] == 1
    rows = await _outbox_rows(db, family_id)
    assert rows[0]["status"] == "PUBLISHED"
    msg = (await db.execute(text("SELECT message_type, service_code FROM doran_messages WHERE family_group_id = :fid"), {"fid": family_id})).one()
    assert msg[0] == "SERVICE_ACTION"
    assert msg[1] == "mark-point"


async def test_outbox_05_transient_failure_then_retryable(family_env):
    db, member, family_id = family_env["db"], family_env["member"], family_env["family_id"]
    # Suspend the Doran subscription so the first delivery attempt fails in a
    # way the Worker must treat as retryable, not permanent.
    await db.execute(text("UPDATE service_subscriptions SET status = 'suspended' WHERE family_group_id = :fid AND service_code = 'doran'"), {"fid": family_id})
    await db.commit()
    await _complete_mission(db, member.player_id)
    result = await worker.run_once(db)
    assert result["retry_scheduled"] == 1
    row = (await _outbox_rows(db, family_id))[0]
    assert row["status"] == "PENDING"
    assert row["attempt_count"] == 1

    await db.execute(text("UPDATE service_subscriptions SET status = 'active' WHERE family_group_id = :fid AND service_code = 'doran'"), {"fid": family_id})
    await db.execute(text("UPDATE service_outbox_events SET next_attempt_at = now() - interval '1 second' WHERE family_id = :fid"), {"fid": family_id})
    await db.commit()
    result2 = await worker.run_once(db)
    assert result2["published"] == 1


async def test_outbox_06_max_attempts_exceeded_dead(family_env):
    db, member, family_id = family_env["db"], family_env["member"], family_env["family_id"]
    await db.execute(text("UPDATE service_subscriptions SET status = 'suspended' WHERE family_group_id = :fid AND service_code = 'doran'"), {"fid": family_id})
    await db.commit()
    await _complete_mission(db, member.player_id)  # subscription stays suspended -> always fails
    for _ in range(outbox_service.MAX_ATTEMPTS):
        await db.execute(text("UPDATE service_outbox_events SET next_attempt_at = now() - interval '1 second' WHERE family_id = :fid"), {"fid": family_id})
        await db.commit()
        await worker.run_once(db)
    row = (await _outbox_rows(db, family_id))[0]
    assert row["status"] == "DEAD"
    assert row["attempt_count"] >= outbox_service.MAX_ATTEMPTS


async def test_outbox_07_two_workers_no_double_claim(family_env):
    db, family_id = family_env["db"], family_env["family_id"]
    for i in range(6):
        await outbox_service.enqueue_event(
            db, owner_service="mark-point", event_type="mission.completed", event_version=1,
            aggregate_type="mission", aggregate_id=str(i), source_event_id=f"concurrent-claim-{i}",
            family_id=family_id, payload={"i": i},
        )
    await db.commit()

    async def claim_with_own_session():
        async with AsyncSessionLocal() as session:
            return [row.id for row in await outbox_service.claim_batch(session, batch_size=3)]

    results = await run_concurrent([claim_with_own_session, claim_with_own_session])
    assert all(not isinstance(r, Exception) for r in results), results
    claimed_a, claimed_b = results
    assert len(claimed_a) == 3 and len(claimed_b) == 3
    assert set(claimed_a).isdisjoint(set(claimed_b))
    assert len(set(claimed_a) | set(claimed_b)) == 6


async def test_outbox_08_expired_lease_recovered(family_env):
    db, family_id = family_env["db"], family_env["family_id"]
    event = await outbox_service.enqueue_event(
        db, owner_service="mark-point", event_type="mission.completed", event_version=1,
        aggregate_type="mission", aggregate_id="99", source_event_id="lease-probe",
        family_id=family_id, payload={},
    )
    await db.commit()
    await db.execute(
        text("UPDATE service_outbox_events SET status='PROCESSING', locked_until = now() - interval '1 minute' WHERE id = :id"),
        {"id": event.id},
    )
    await db.commit()
    claimed = await outbox_service.claim_batch(db, batch_size=10)
    assert event.id in [row.id for row in claimed]


async def test_outbox_09_and_10_publish_then_crash_then_converges(family_env):
    db, member, family_id = family_env["db"], family_env["member"], family_env["family_id"]
    await _complete_mission(db, member.player_id)
    row = (await _outbox_rows(db, family_id))[0]

    # Simulate: Doran already durably has the message (call the same publish
    # path the Worker would use), but the Worker crashes before marking its
    # own Outbox row PUBLISHED - the row is still PENDING here.
    principal = await doran_service.bootstrap_service_principal(db, "mark-point", "Mark Point")
    binding = await doran_service.ensure_canonical_service_binding(db, principal, family_id, worker.ALLOWED_ACTIONS_BY_OWNER["mark-point"])
    from app.domains.doran.schemas import ServiceActionPublish
    publish_data = ServiceActionPublish(
        room_id=binding.room_id, action_type=row["event_type"], schema_version=1,
        source=row["owner_service"], source_event_id=row["source_event_id"], snapshot=row["payload"],
    )
    await doran_service.publish_service_action(db, principal, family_id, publish_data)
    count_before_retry = (await db.execute(text("SELECT count(*) FROM doran_messages WHERE family_group_id = :fid"), {"fid": family_id})).scalar_one()
    assert count_before_retry == 1

    # Retry: the Worker doesn't know delivery already happened - it retries
    # with the same stored source_event_id, hits Doran idempotency, and this
    # time successfully marks its own row PUBLISHED.
    result = await worker.run_once(db)
    assert result["published"] == 1
    final_row = (await _outbox_rows(db, family_id))[0]
    assert final_row["status"] == "PUBLISHED"
    count_after_retry = (await db.execute(text("SELECT count(*) FROM doran_messages WHERE family_group_id = :fid"), {"fid": family_id})).scalar_one()
    assert count_after_retry == 1


# ---------------------------------------------------------------------------
# SERVICE Room self-onboarding 11-17
# ---------------------------------------------------------------------------

async def _bind_mark_point(db, family_id: int) -> tuple:
    principal = await doran_service.bootstrap_service_principal(db, "mark-point", "Mark Point")
    binding = await doran_service.ensure_canonical_service_binding(db, principal, family_id, worker.ALLOWED_ACTIONS_BY_OWNER["mark-point"])
    return principal, binding


async def test_room_11_self_onboarding(family_env):
    db, client, member, family_id = family_env["db"], family_env["client"], family_env["member"], family_env["family_id"]
    await _bind_mark_point(db, family_id)
    resp = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=member.headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["service_code"] == "mark-point"
    assert body["status"] == "active"


async def test_room_12_repeat_call_one_participant(family_env):
    db, client, member, family_id = family_env["db"], family_env["client"], family_env["member"], family_env["family_id"]
    _, binding = await _bind_mark_point(db, family_id)
    first = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=member.headers)
    second = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=member.headers)
    assert first.json()["participant_id"] == second.json()["participant_id"]
    count = (
        await db.execute(
            text("SELECT count(*) FROM doran_participants WHERE room_id = :rid AND status = 'active'"),
            {"rid": str(binding.room_id)},
        )
    ).scalar_one()
    assert count == 1


async def test_room_13_other_family_denied(family_env):
    db, client, member = family_env["db"], family_env["client"], family_env["member"]
    other_family_id = await create_family(db, "Other Onboard Family")
    await set_subscription(db, other_family_id, "active")
    await _bind_mark_point(db, other_family_id)
    resp = await client.post(f"/api/families/{other_family_id}/doran/services/mark-point/room", headers=member.headers)
    assert resp.status_code == 403


async def test_room_14_inactive_membership_denied(family_env):
    db, client, family_id = family_env["db"], family_env["client"], family_env["family_id"]
    await _bind_mark_point(db, family_id)
    suspended = await create_actor(db, family_id, name="suspended-member", service_role="participant", membership_status="suspended")
    resp = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=suspended.headers)
    assert resp.status_code == 403


async def test_room_15_inactive_subscription_denied(family_env):
    db, client, member, family_id = family_env["db"], family_env["client"], family_env["member"], family_env["family_id"]
    await _bind_mark_point(db, family_id)
    await db.execute(text("UPDATE service_subscriptions SET status = 'suspended' WHERE family_group_id = :fid AND service_code = 'doran'"), {"fid": family_id})
    await db.commit()
    resp = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=member.headers)
    assert resp.status_code == 403


async def test_room_16_inactive_binding_denied(family_env):
    db, client, member, family_id = family_env["db"], family_env["client"], family_env["member"], family_env["family_id"]
    _, binding = await _bind_mark_point(db, family_id)
    await doran_service.set_service_binding_status(db, binding.id, "inactive")
    resp = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=member.headers)
    assert resp.status_code == 404


async def test_room_17_non_service_room_binding_db_blocked(family_env):
    db, family_id = family_env["db"], family_env["family_id"]
    principal = await doran_service.bootstrap_service_principal(db, "mark-point", "Mark Point")
    group_room_id = (
        await db.execute(
            text(
                "INSERT INTO doran_rooms (id, family_group_id, room_type, status, created_by_actor_type, next_message_sequence, version) "
                "VALUES (gen_random_uuid(), :fid, 'GROUP', 'active', 'SYSTEM', 0, 1) RETURNING id"
            ),
            {"fid": family_id},
        )
    ).scalar_one()
    await db.commit()
    with pytest.raises(Exception):
        await db.execute(
            text(
                "INSERT INTO doran_service_bindings (service_principal_id, family_group_id, room_id, allowed_actions, status) "
                "VALUES (:pid, :fid, :rid, '[]'::jsonb, 'active')"
            ),
            {"pid": principal.id, "fid": family_id, "rid": group_room_id},
        )
    await db.rollback()


# ---------------------------------------------------------------------------
# Ingress security / limits 18-22
# ---------------------------------------------------------------------------

async def test_limit_18_32kb_or_under_allowed(service_env):
    client, family_id, svc = service_env["client"], service_env["family_id"], service_env["service"]
    padding = "x" * (30 * 1024)
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={
            "room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
            "source": "mission-svc", "source_event_id": "evt-size-ok", "snapshot": {}, "padding": padding,
        },
        headers=svc.headers,
    )
    assert resp.status_code == 201, resp.text
    assert "padding" not in resp.json().get("service_payload", {})


async def test_limit_19_over_32kb_rejected_413(service_env):
    client, family_id, svc = service_env["client"], service_env["family_id"], service_env["service"]
    padding = "x" * (40 * 1024)
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={
            "room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
            "source": "mission-svc", "source_event_id": "evt-size-over", "snapshot": {}, "padding": padding,
        },
        headers=svc.headers,
    )
    assert resp.status_code == 413


async def test_limit_20_length_unaware_stream_still_capped():
    from starlette.requests import Request
    from app.domains.doran.ingress_limits import enforce_service_body_limit, MAX_SERVICE_INGRESS_BYTES

    chunk = b"a" * 1024
    chunk_count = (MAX_SERVICE_INGRESS_BYTES // len(chunk)) + 5  # total > cap, no Content-Length at all

    async def receive():
        nonlocal chunk_count
        if chunk_count > 0:
            chunk_count -= 1
            return {"type": "http.request", "body": chunk, "more_body": chunk_count > 0}
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {"type": "http", "headers": []}  # deliberately no content-length header
    request = Request(scope, receive)
    with pytest.raises(Exception) as exc_info:
        await enforce_service_body_limit(request)
    assert getattr(exc_info.value, "status_code", None) == 413


async def test_limit_21_unknown_credential_runs_dummy_bcrypt(service_env, monkeypatch):
    from app.domains.doran import service_actor

    calls = []
    real_checkpw = service_actor.bcrypt.checkpw

    def spy(secret_bytes, hash_bytes):
        calls.append(hash_bytes)
        return real_checkpw(secret_bytes, hash_bytes)

    monkeypatch.setattr(service_actor.bcrypt, "checkpw", spy)

    client, family_id, svc = service_env["client"], service_env["family_id"], service_env["service"]
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "s", "source_event_id": "e", "snapshot": {}},
        headers={"Authorization": "Bearer unknown-credential-id.some-secret"},
    )
    assert resp.status_code == 401
    assert calls, "unknown credential_id must still pay a bcrypt.checkpw cost (dummy hash)"
    assert calls[0] == service_actor._DUMMY_CREDENTIAL_HASH.encode("utf-8")


async def test_limit_22_wrong_secret_and_revoked_regression(service_env):
    from tests.conftest import service_headers
    client, db, family_id, svc = service_env["client"], service_env["db"], service_env["family_id"], service_env["service"]
    wrong = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "s", "source_event_id": "e1", "snapshot": {}},
        headers=service_headers(svc.credential_id, "wrong-secret"),
    )
    assert wrong.status_code == 401
    await doran_service.revoke_service_principal(db, svc.principal_id)
    revoked = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "s", "source_event_id": "e2", "snapshot": {}},
        headers=svc.headers,
    )
    assert revoked.status_code == 401


# ---------------------------------------------------------------------------
# E2E 23-28: 실제 미션 완료 -> Outbox -> Worker -> Doran -> 사용자 조회
# ---------------------------------------------------------------------------

async def test_e2e_23_to_28_mission_completion_to_visible_message(family_env):
    db, client, member, family_id = family_env["db"], family_env["client"], family_env["member"], family_env["family_id"]

    # 23. 미션 완료 + 포인트 확정
    mission = await _complete_mission(db, member.player_id, point=100, text_="설거지")
    total_earned = (await db.execute(text("SELECT total_earned FROM players WHERE id = :pid"), {"pid": member.player_id})).scalar_one()
    assert total_earned == 100
    assert mission.status == "completed"

    # 24. Outbox row 생성
    rows = await _outbox_rows(db, family_id)
    assert len(rows) == 1
    assert rows[0]["payload"]["mission_title"] == "설거지"
    assert rows[0]["payload"]["awarded_points"] == 100

    # 25. Worker 발행
    result = await worker.run_once(db)
    assert result["published"] == 1

    # 26. 사용자 SERVICE Room onboarding
    onboard = await client.post(f"/api/families/{family_id}/doran/services/mark-point/room", headers=member.headers)
    assert onboard.status_code == 200
    room_id = onboard.json()["room_id"]

    # 27. GET messages에서 mission.completed 확인
    visible = await client.get(f"/api/families/{family_id}/doran/rooms/{room_id}/messages", headers=member.headers)
    assert visible.status_code == 200
    items = visible.json()["items"]
    service_items = [m for m in items if m["message_type"] == "SERVICE_ACTION"]
    assert len(service_items) == 1
    assert service_items[0]["service_code"] == "mark-point"
    assert service_items[0]["service_payload"]["snapshot"]["mission_title"] == "설거지"
    assert service_items[0]["service_payload"]["snapshot"]["awarded_points"] == 100
    assert service_items[0]["service_payload"]["snapshot"]["player_display_name"] == "member"

    # 28. Worker 재실행 후 중복 메시지 없음
    result2 = await worker.run_once(db)
    assert result2["claimed"] == 0
    count = (await db.execute(text("SELECT count(*) FROM doran_messages WHERE family_group_id = :fid AND message_type = 'SERVICE_ACTION'"), {"fid": family_id})).scalar_one()
    assert count == 1
