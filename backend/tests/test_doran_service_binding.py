"""PHASE2-DORAN-R2B1-SERVICE-ACTOR-AND-BINDING-001 real-PostgreSQL suite.

Covers the 17 required items from the R2-B1 handoff (migration up/down/re-up
and the R2-A 17-test regression are exercised separately as part of the full
regression run, not duplicated here) plus the four early-PM demo scenarios
(A: normal publish, B: cross-Family/unbound denial, C: replay dedup,
D: a service cannot impersonate a user TEXT sender).
"""
from __future__ import annotations

import bcrypt
import pytest
from sqlalchemy import text

from app.domains.doran import service as doran_service
from tests.conftest import create_family, create_service_actor, run_concurrent, service_headers, set_subscription


async def _counts(db, *tables: str) -> dict[str, int]:
    out = {}
    for t in tables:
        out[t] = (await db.execute(text(f"SELECT count(*) FROM {t}"))).scalar_one()
    return out


# ---------------------------------------------------------------------------
# 1. user JWT rejected by the service ingress
# ---------------------------------------------------------------------------

async def test_01_user_jwt_blocked_from_service_ingress(service_env):
    client, family_id = service_env["client"], service_env["family_id"]
    svc = service_env["service"]
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=service_env["admin"].headers,
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 2. invalid credential blocked
# ---------------------------------------------------------------------------

async def test_02_invalid_credential_blocked(service_env):
    client, family_id = service_env["client"], service_env["family_id"]
    svc = service_env["service"]
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=service_headers(svc.credential_id, "wrong-secret"),
    )
    assert resp.status_code == 401
    resp2 = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=service_headers("unknown-credential-id", svc.secret),
    )
    assert resp2.status_code == 401


# ---------------------------------------------------------------------------
# 3. revoked principal blocked immediately
# ---------------------------------------------------------------------------

async def test_03_revoked_principal_blocked(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    await doran_service.revoke_service_principal(db, svc.principal_id)
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 4. a different Service Principal (different service scope) has no access
#    to a Room it isn't bound to, even with a valid, active credential
# ---------------------------------------------------------------------------

async def test_04_different_service_scope_blocked(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    mission_actor = service_env["service"]
    point_actor = await create_service_actor(db, family_id, service_code="point", name="point-service",
                                              allowed_actions=[{"action_type": "point_awarded", "schema_version": 1}])
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(mission_actor.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "point-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=point_actor.headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 5. a Binding in a different Family denies cross-Family publish
# ---------------------------------------------------------------------------

async def test_05_different_family_binding_blocked(service_env):
    client, db = service_env["client"], service_env["db"]
    svc = service_env["service"]
    other_family_id = await create_family(db, "Other Family")
    await set_subscription(db, other_family_id, "active")
    other_actor = await create_service_actor(db, other_family_id, service_code="mission", name="mission-service-2")
    resp = await client.post(
        f"/api/families/{other_family_id}/doran/service/actions",
        json={"room_id": str(other_actor.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 6. inactive Family Doran subscription blocks publish
# ---------------------------------------------------------------------------

async def test_06_inactive_subscription_blocked(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    await db.execute(text("UPDATE service_subscriptions SET status = 'suspended' WHERE family_group_id = :fid AND service_code = 'doran'"), {"fid": family_id})
    await db.commit()
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 7. inactive Binding blocks publish
# ---------------------------------------------------------------------------

async def test_07_inactive_binding_blocked(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    await doran_service.set_service_binding_status(db, svc.binding_id, "inactive")
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 8. publishing into a non-SERVICE Room is blocked (defense in depth). As of
#    R2-B2 this is enforced twice: publish_service_action() re-checks
#    room.room_type at request time (still true below via the app-layer
#    check on an inactive/non-existent Binding), and
#    fn_doran_service_binding_room_guard (migration 0004) now refuses to let
#    such a Binding row exist in the database at all - the raw-SQL bypass
#    this test used to use to construct the scenario is itself blocked.
# ---------------------------------------------------------------------------

async def test_08_non_service_room_publish_blocked(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    group_room = await client.post(
        f"/api/families/{family_id}/doran/rooms",
        json={"room_type": "GROUP", "title": "not-a-service-room", "participant_membership_ids": [service_env["member"].membership_id]},
        headers=service_env["admin"].headers,
    )
    group_room_id = group_room.json()["id"]
    with pytest.raises(Exception, match="must reference a SERVICE Room"):
        await db.execute(
            text("INSERT INTO doran_service_bindings (service_principal_id, family_group_id, room_id, allowed_actions, status) "
                 "VALUES (:pid, :fid, :rid, '[{\"action_type\": \"mission_approved\", \"schema_version\": 1}]'::jsonb, 'active')"),
            {"pid": svc.principal_id, "fid": family_id, "rid": group_room_id},
        )
    await db.rollback()

    # Publishing against a Room no Binding was ever created for is still
    # blocked the ordinary way (app-layer binding lookup finds nothing).
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": group_room_id, "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 9. disallowed action schema blocked
# ---------------------------------------------------------------------------

async def test_09_disallowed_action_schema_blocked(service_env):
    client, family_id = service_env["client"], service_env["family_id"]
    svc = service_env["service"]
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_rejected", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 422
    resp2 = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 2,
              "source": "mission-svc", "source_event_id": "evt-2", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp2.status_code == 422


# ---------------------------------------------------------------------------
# 10. normal SERVICE_ACTION publish succeeds
# ---------------------------------------------------------------------------

async def test_10_normal_service_action_publish(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-1", "snapshot": {"mission": "wash dishes", "points": 10}},
        headers=svc.headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["message_type"] == "SERVICE_ACTION"
    assert body["sender_participant_id"] is None
    assert body["service_code"] == "mission"
    assert body["service_payload_version"] == 1
    assert body["service_payload"]["action_type"] == "mission_approved"
    assert body["service_payload"]["snapshot"] == {"mission": "wash dishes", "points": 10}
    assert body["sequence"] == 1

    row = (await db.execute(text("SELECT message_type, sender_participant_id, service_principal_id FROM doran_messages WHERE id = :id"), {"id": body["id"]})).one()
    assert row[0] == "SERVICE_ACTION"
    assert row[1] is None
    assert row[2] == svc.principal_id


# ---------------------------------------------------------------------------
# 11. sequential replay of the same event is idempotent
# ---------------------------------------------------------------------------

async def test_11_sequential_replay_idempotent(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    payload = {"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
               "source": "mission-svc", "source_event_id": "evt-replay", "snapshot": {"points": 5}}
    first = await client.post(f"/api/families/{family_id}/doran/service/actions", json=payload, headers=svc.headers)
    second = await client.post(f"/api/families/{family_id}/doran/service/actions", json=payload, headers=svc.headers)
    third = await client.post(f"/api/families/{family_id}/doran/service/actions", json=payload, headers=svc.headers)
    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 201
    ids = {first.json()["id"], second.json()["id"], third.json()["id"]}
    sequences = {first.json()["sequence"], second.json()["sequence"], third.json()["sequence"]}
    assert len(ids) == 1
    assert len(sequences) == 1
    count = (await db.execute(
        text("SELECT count(*) FROM doran_messages WHERE service_principal_id = :pid AND source = 'mission-svc' AND source_event_id = 'evt-replay'"),
        {"pid": svc.principal_id},
    )).scalar_one()
    assert count == 1


# ---------------------------------------------------------------------------
# 12. concurrent replay (>= 8 workers) of the same event is idempotent
# ---------------------------------------------------------------------------

async def test_12_concurrent_replay_idempotent(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    payload = {"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
               "source": "mission-svc", "source_event_id": "evt-concurrent", "snapshot": {"points": 7}}

    async def send():
        return await client.post(f"/api/families/{family_id}/doran/service/actions", json=payload, headers=svc.headers)

    results = await run_concurrent([send for _ in range(8)])
    assert all(not isinstance(r, Exception) for r in results), results
    assert all(r.status_code != 500 for r in results), [r.status_code for r in results]
    assert all(r.status_code == 201 for r in results), [r.status_code for r in results]

    ids = {r.json()["id"] for r in results}
    sequences = {r.json()["sequence"] for r in results}
    assert len(ids) == 1, f"expected one converged message id, got {ids}"
    assert len(sequences) == 1, f"expected one converged sequence, got {sequences}"

    count = (await db.execute(
        text("SELECT count(*) FROM doran_messages WHERE service_principal_id = :pid AND source = 'mission-svc' AND source_event_id = 'evt-concurrent'"),
        {"pid": svc.principal_id},
    )).scalar_one()
    assert count == 1

    audit_result_codes = list((await db.execute(
        text("SELECT result_code FROM doran_service_audit_log WHERE service_principal_id = :pid AND room_id = :rid AND event_type IN ('publish_success', 'replay_detected') ORDER BY created_at"),
        {"pid": svc.principal_id, "rid": str(svc.room_id)},
    )).scalars())
    assert audit_result_codes.count("success") == 1
    assert audit_result_codes.count("idempotent") == 7


# ---------------------------------------------------------------------------
# 13. same key, different payload -> 409, DB invariant
# ---------------------------------------------------------------------------

async def test_13_same_key_different_payload_conflict(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    first = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-conflict", "snapshot": {"points": 5}},
        headers=svc.headers,
    )
    assert first.status_code == 201
    second = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-conflict", "snapshot": {"points": 999}},
        headers=svc.headers,
    )
    assert second.status_code == 409
    row = (await db.execute(
        text("SELECT count(*), max((service_payload->>'snapshot')::text) FILTER (WHERE service_payload->'snapshot'->>'points' = '5') "
             "FROM doran_messages WHERE service_principal_id = :pid AND source_event_id = 'evt-conflict'"),
        {"pid": svc.principal_id},
    )).one()
    assert row[0] == 1


# ---------------------------------------------------------------------------
# 14. denied requests leave the DB unchanged
# ---------------------------------------------------------------------------

async def test_14_denied_request_db_invariant(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    before = await _counts(db, "doran_messages", "doran_service_bindings", "service_principals")
    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "not_allowed", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-denied", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 422
    after = await _counts(db, "doran_messages", "doran_service_bindings", "service_principals")
    assert before == after


# ---------------------------------------------------------------------------
# 15. audit log never stores the secret/credential or message body
# ---------------------------------------------------------------------------

async def test_15_audit_log_excludes_secrets_and_body(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    sensitive_snapshot = {"note": "sensitive-body-marker-should-not-leak"}
    await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-audit", "snapshot": sensitive_snapshot},
        headers=svc.headers,
    )
    rows = list((await db.execute(text("SELECT event_type, result_code, detail FROM doran_service_audit_log"))).all())
    assert len(rows) >= 1
    dump = str(rows)
    assert svc.secret not in dump
    assert "sensitive-body-marker-should-not-leak" not in dump
    assert bcrypt.checkpw(svc.secret.encode(), (await db.execute(text("SELECT credential_hash FROM service_principals WHERE id = :id"), {"id": svc.principal_id})).scalar_one().encode())


# ---------------------------------------------------------------------------
# Early PM demonstration scenarios (A-D)
# ---------------------------------------------------------------------------

async def test_scenario_A_normal_publish_into_bound_room(service_env):
    """A SERVICE Room has no human-participant bootstrap API in this phase
    (create_room's SERVICE branch stays 422 "not available in v1" - Binding
    creation is the only way a SERVICE Room comes to exist at all, and it
    creates no human Participants). To demonstrate a human can actually see
    the published event, this test adds the admin as a Participant via direct
    fixture setup - the same kind of test-only setup already used for the
    non-SERVICE-room defense-in-depth check above, not a production API path."""
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    admin = service_env["admin"]
    await db.execute(
        text(
            "INSERT INTO doran_participants (family_group_id, room_id, family_membership_id, room_role, status, joined_sequence) "
            "VALUES (:fid, :rid, :mid, 'member', 'active', 0)"
        ),
        {"fid": family_id, "rid": str(svc.room_id), "mid": admin.membership_id},
    )
    await db.commit()

    resp = await client.post(
        f"/api/families/{family_id}/doran/service/actions",
        json={"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-scenario-a", "snapshot": {"points": 10}},
        headers=svc.headers,
    )
    assert resp.status_code == 201
    visible = await client.get(
        f"/api/families/{family_id}/doran/rooms/{svc.room_id}/messages",
        headers=admin.headers,
    )
    assert visible.status_code == 200
    assert any(m["message_type"] == "SERVICE_ACTION" for m in visible.json()["items"])


async def test_scenario_B_other_family_or_unbound_room_denied(service_env):
    client, db = service_env["client"], service_env["db"]
    svc = service_env["service"]
    other_family_id = await create_family(db, "Scenario B Family")
    await set_subscription(db, other_family_id, "active")
    other_actor = await create_service_actor(db, other_family_id)
    resp = await client.post(
        f"/api/families/{other_family_id}/doran/service/actions",
        json={"room_id": str(other_actor.room_id), "action_type": "mission_approved", "schema_version": 1,
              "source": "mission-svc", "source_event_id": "evt-scenario-b", "snapshot": {}},
        headers=svc.headers,
    )
    assert resp.status_code == 404


async def test_scenario_C_resend_creates_no_duplicate(service_env):
    client, db, family_id = service_env["client"], service_env["db"], service_env["family_id"]
    svc = service_env["service"]
    payload = {"room_id": str(svc.room_id), "action_type": "mission_approved", "schema_version": 1,
               "source": "mission-svc", "source_event_id": "evt-scenario-c", "snapshot": {"points": 3}}
    first = await client.post(f"/api/families/{family_id}/doran/service/actions", json=payload, headers=svc.headers)
    resend = await client.post(f"/api/families/{family_id}/doran/service/actions", json=payload, headers=svc.headers)
    assert first.status_code == 201 and resend.status_code == 201
    assert first.json()["id"] == resend.json()["id"]
    count = (await db.execute(text("SELECT count(*) FROM doran_messages WHERE source_event_id = 'evt-scenario-c'"))).scalar_one()
    assert count == 1


async def test_scenario_D_service_cannot_impersonate_user_text_sender(service_env):
    client, family_id = service_env["client"], service_env["family_id"]
    svc = service_env["service"]
    resp = await client.post(
        f"/api/families/{family_id}/doran/rooms/{svc.room_id}/messages",
        json={"client_message_id": "impersonation-attempt", "body": "pretending to be a person"},
        headers=svc.headers,
    )
    assert resp.status_code == 401
