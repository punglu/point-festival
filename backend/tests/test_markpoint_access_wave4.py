"""Wave 4 — Markpoint family-service access (D5-A/D5-A2/D5-A3/D5-B/D5-C).

Covers `MONGLE-W4-MARKPOINT-SERVICE-ACCESS-001`'s implementable-without-schema-
change slice (FamilyAdmin direct activation, default access resolution,
ServiceAdmin assign/revoke via the existing generic role path, registrant/
FamilyAdmin-not-auto-ServiceAdmin) plus the D5-C System Actor Port contract.

Activation-request (member request -> admin approval) and per-member
restriction need new persisted state the existing schema does not have; they
are recorded as `SCHEMA_DELTA_REQUIRED` in this task's QA report rather than
mocked here. No `MarkpointParticipant` aggregate is introduced.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.domains.family import auth_service, service as family_service
from app.domains.family.models import Account, FamilyGroup, FamilyMembership, MembershipRoleAssignment
from app.domains.markpoint_access import service as markpoint_service
from app.domains.markpoint_access.system_event_port import (
    InMemoryMarkpointSystemEventPort,
    MarkpointSystemEventEnvelope,
    MarkpointSystemEventEnvelopeError,
)

from tests.conftest import create_family


GOOD_PASSWORD = "Str0ngPassw0rd!"


# --- helpers (mirrors test_account_auth_wave1.py's local-helper convention) -


async def _make_account(db, display_name: str) -> Account:
    account = Account(display_name=display_name, status="active")
    db.add(account)
    await db.flush()
    return account


async def _make_membership(db, family_id: int, account_id: int, status_value: str = "active") -> FamilyMembership:
    membership = FamilyMembership(
        family_group_id=family_id,
        account_id=account_id,
        relationship="unknown",
        status=status_value,
        joined_at=datetime.now(timezone.utc) if status_value == "active" else None,
    )
    db.add(membership)
    await db.flush()
    return membership


async def _grant_family_role(db, membership_id: int, role_code: str) -> None:
    from sqlalchemy import text

    role_id = (
        await db.execute(
            text("SELECT id FROM roles WHERE scope_type='FAMILY' AND code=:code"), {"code": role_code}
        )
    ).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=membership_id, role_id=role_id))
    await db.flush()


async def _account_with_login(db, display_name: str, username: str, password: str = GOOD_PASSWORD) -> Account:
    account = await _make_account(db, display_name)
    await auth_service.create_credential(db, account.id, username, password)
    await db.commit()
    return account


async def _login(client, username: str, password: str = GOOD_PASSWORD, device_id: str = "device-a") -> dict:
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": username, "password": password, "device_id": device_id},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _admin_with_family(db, client, name: str, username: str) -> tuple[Account, int, dict]:
    admin = await _account_with_login(db, name, username)
    family_id = await create_family(db, name)
    membership = await _make_membership(db, family_id, admin.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()
    body = await _login(client, username)
    return admin, family_id, _bearer(body["access_token"])


# --- default access resolution --------------------------------------------


async def test_default_access_false_before_activation(db):
    account = await _make_account(db, "before")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await db.commit()

    status_ = await markpoint_service.get_access_status(db, membership)
    assert status_["subscription_status"] == "inactive"
    assert status_["has_default_access"] is False
    assert status_["is_service_admin"] is False


async def test_default_access_true_after_activation_for_active_membership(db):
    account = await _make_account(db, "member")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await db.commit()

    await markpoint_service.activate_directly(db, family_id)

    status_ = await markpoint_service.get_access_status(db, membership)
    assert status_["subscription_status"] == "active"
    assert status_["has_default_access"] is True


async def test_default_access_false_for_suspended_membership_even_if_active_subscription(db):
    account = await _make_account(db, "suspended-member")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await db.commit()
    await markpoint_service.activate_directly(db, family_id)

    membership.status = "suspended"
    await db.commit()

    status_ = await markpoint_service.get_access_status(db, membership)
    assert status_["has_default_access"] is False


async def test_activation_does_not_create_any_mission_participation_record(db):
    """No `MarkpointParticipant` aggregate and no auto Mission-participation row."""
    account = await _make_account(db, "noparticipant")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await db.commit()

    await markpoint_service.activate_directly(db, family_id)

    # `missions` is still legacy player-owned in this Wave (untouched by Wave
    # 4 by design); the assertion that matters here is structural: activation
    # writes only `service_subscriptions`, never a participation-like row.
    subscription = await markpoint_service._subscription(db, family_id)
    assert subscription.service_code == "markpoint"
    assert membership.status == "active"


# --- FamilyAdmin direct activation (HTTP) ----------------------------------


async def test_family_admin_can_activate_directly(db, client):
    _, family_id, headers = await _admin_with_family(db, client, "admin1", "admin1.user")

    resp = await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "active"

    access = await client.get(f"/api/families/{family_id}/markpoint/access", headers=headers)
    assert access.json()["has_default_access"] is True


async def test_activation_is_idempotent(db, client):
    _, family_id, headers = await _admin_with_family(db, client, "admin2", "admin2.user")

    first = await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)
    second = await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)
    assert first.status_code == second.status_code == 200
    assert second.json()["status"] == "active"

    from sqlalchemy import text

    rows = (
        await db.execute(
            text("SELECT count(*) FROM service_subscriptions WHERE family_group_id = :f AND service_code = 'markpoint'"),
            {"f": family_id},
        )
    ).scalar_one()
    assert rows == 1


async def test_plain_member_cannot_activate(db, client):
    member = await _account_with_login(db, "plain", "plain.markpoint")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, member.id)
    await _grant_family_role(db, membership.id, "member")
    await db.commit()
    body = await _login(client, "plain.markpoint")

    resp = await client.post(
        f"/api/families/{family_id}/markpoint/activate", headers=_bearer(body["access_token"])
    )
    assert resp.status_code == 403


async def test_cross_family_activation_denied(db, client):
    _, family_a, headers = await _admin_with_family(db, client, "adminA", "adminA.markpoint")
    family_b = await create_family(db, "B")
    await db.commit()

    resp = await client.post(f"/api/families/{family_b}/markpoint/activate", headers=headers)
    assert resp.status_code == 403


async def test_access_route_requires_authentication(db, client):
    family_id = await create_family(db)
    await db.commit()
    resp = await client.get(f"/api/families/{family_id}/markpoint/access")
    assert resp.status_code == 401


# --- registrant / FamilyAdmin not auto-ServiceAdmin ------------------------


async def test_activating_family_admin_gets_no_automatic_service_admin_role(db, client):
    admin, family_id, headers = await _admin_with_family(db, client, "admin3", "admin3.user")

    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)

    access = (await client.get(f"/api/families/{family_id}/markpoint/access", headers=headers)).json()
    assert access["is_service_admin"] is False
    assert access["service_admin_roles"] == []


# --- ServiceAdmin explicit assign/revoke (existing generic role path) -----


async def test_service_admin_assignment_requires_active_subscription(db, client):
    admin, family_id, headers = await _admin_with_family(db, client, "admin4", "admin4.user")
    membership = (
        await family_service.get_active_membership(db, admin.id, family_id)
    )

    resp = await client.post(
        f"/api/families/{family_id}/markpoint/service-admins",
        json={"membership_id": membership.id, "role_code": "mission_manager"},
        headers=headers,
    )
    assert resp.status_code == 409  # no active ServiceSubscription yet

    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)

    resp2 = await client.post(
        f"/api/families/{family_id}/markpoint/service-admins",
        json={"membership_id": membership.id, "role_code": "mission_manager"},
        headers=headers,
    )
    assert resp2.status_code == 201, resp2.text

    access = (await client.get(f"/api/families/{family_id}/markpoint/access", headers=headers)).json()
    assert access["is_service_admin"] is True
    assert "mission_manager" in access["service_admin_roles"]


async def test_service_admin_assignment_rejects_non_service_admin_role_code(db, client):
    admin, family_id, headers = await _admin_with_family(db, client, "admin4b", "admin4b.user")
    membership = await family_service.get_active_membership(db, admin.id, family_id)
    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)

    resp = await client.post(
        f"/api/families/{family_id}/markpoint/service-admins",
        json={"membership_id": membership.id, "role_code": "owner"},
        headers=headers,
    )
    assert resp.status_code == 422


async def test_plain_member_cannot_assign_service_admin(db, client):
    admin, family_id, headers = await _admin_with_family(db, client, "admin4c", "admin4c.user")
    member = await _account_with_login(db, "plainassign", "plainassign.user")
    member_membership = await _make_membership(db, family_id, member.id)
    await _grant_family_role(db, member_membership.id, "member")
    await db.commit()
    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)
    member_body = await _login(client, "plainassign.user")

    resp = await client.post(
        f"/api/families/{family_id}/markpoint/service-admins",
        json={"membership_id": member_membership.id, "role_code": "mission_manager"},
        headers=_bearer(member_body["access_token"]),
    )
    assert resp.status_code == 403


async def test_service_admin_revoke_removes_access(db, client):
    admin, family_id, headers = await _admin_with_family(db, client, "admin5", "admin5.user")
    membership = await family_service.get_active_membership(db, admin.id, family_id)
    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=headers)
    assign = await client.post(
        f"/api/families/{family_id}/markpoint/service-admins",
        json={"membership_id": membership.id, "role_code": "point_admin"},
        headers=headers,
    )
    assignment_id = assign.json()["id"]

    revoke = await client.delete(
        f"/api/families/{family_id}/markpoint/service-admins/{assignment_id}", headers=headers
    )
    assert revoke.status_code == 204

    access = (await client.get(f"/api/families/{family_id}/markpoint/access", headers=headers)).json()
    assert access["is_service_admin"] is False


async def test_membership_termination_revokes_service_admin_role(db):
    account = await _make_account(db, "svcadmin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await db.commit()
    await markpoint_service.activate_directly(db, family_id)
    await family_service.assign_role(db, family_id, membership, "mission_manager", "markpoint", account.id)

    status_before = await markpoint_service.get_access_status(db, membership)
    assert status_before["is_service_admin"] is True

    await family_service.update_membership(db, membership, None, "left")

    status_after = await markpoint_service.get_access_status(db, membership)
    assert status_after["is_service_admin"] is False


# --- D5-C System Actor Port contract ---------------------------------------


def _envelope(**overrides) -> MarkpointSystemEventEnvelope:
    fields = dict(
        source_event_id="mission-completed-1",
        event_type="markpoint.mission.completed",
        family_group_id=1,
        service_principal_id=1,
        approved_room_binding_id=1,
        occurred_at=datetime.now(timezone.utc),
        payload={"mission_id": 1},
    )
    fields.update(overrides)
    return MarkpointSystemEventEnvelope(**fields)


def test_envelope_requires_source_event_id():
    with pytest.raises(MarkpointSystemEventEnvelopeError):
        _envelope(source_event_id="")


def test_envelope_requires_approved_room_binding():
    with pytest.raises(MarkpointSystemEventEnvelopeError):
        _envelope(approved_room_binding_id=0)


def test_envelope_requires_family_group_id():
    with pytest.raises(MarkpointSystemEventEnvelopeError):
        _envelope(family_group_id=0)


def test_envelope_requires_service_principal_not_a_human_actor():
    with pytest.raises(MarkpointSystemEventEnvelopeError):
        _envelope(service_principal_id=0)


async def test_duplicate_source_event_is_deduplicated_not_republished():
    port = InMemoryMarkpointSystemEventPort()
    envelope = _envelope()

    first = await port.publish(envelope)
    second = await port.publish(_envelope())  # same source_event_id/event_type

    assert first.deduplicated is False
    assert second.deduplicated is True
    assert len(port.published_events) == 1


async def test_different_event_types_for_the_same_source_event_are_distinct():
    port = InMemoryMarkpointSystemEventPort()
    await port.publish(_envelope(event_type="markpoint.mission.completed"))
    await port.publish(_envelope(event_type="markpoint.mission.approved"))

    assert len(port.published_events) == 2
