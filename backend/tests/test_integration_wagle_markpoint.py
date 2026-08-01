"""Integration slice: Wagle naming migration, Markpoint access lifecycle, relay.

Covers `MONGLE-PARALLEL-W2-W4-INTEGRATION-COMPLETION-001`:

- the runtime carries no historical `doran` identifier after migration 0007,
- Markpoint activation request -> FamilyAdmin approve/reject,
- per-member restriction and restore,
- Markpoint -> Wagle system-event relay through the port/adapter boundary.

Every fixture is synthetic and lives in the isolated test database.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import select, text

from app.domains.family.models import FamilyMembership, MembershipRoleAssignment
from app.domains.markpoint_access import service as markpoint_service
from app.domains.markpoint_access.models import (
    MarkpointAccessRestriction, MarkpointActivationRequest,
)
from app.domains.markpoint_access.system_event_port import (
    MarkpointSystemEventEnvelope, MarkpointSystemEventEnvelopeError,
)
from app.domains.markpoint_access.wagle_relay_adapter import WagleMarkpointSystemEventAdapter

from tests.conftest import create_actor, create_family, create_service_actor

# Built from parts so a repository-wide rename sweep cannot silently invert the
# naming assertions in this file — that already happened once.
HISTORICAL = "do" + "ran"


# --- helpers --------------------------------------------------------------


async def _grant_family_role(db, membership_id: int, role_code: str) -> None:
    role_id = (
        await db.execute(
            text("SELECT id FROM roles WHERE scope_type='FAMILY' AND code=:c"), {"c": role_code}
        )
    ).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=membership_id, role_id=role_id))
    await db.commit()


async def _account_login(client, db, family_id, name, *, role: str | None = None):
    """A member of `family_id` with an Account-native session, optionally a
    FamilyAdmin. Returns (membership_id, auth headers)."""
    from app.domains.family import auth_service
    from app.domains.family.models import Account

    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    await auth_service.create_credential(db, account.id, f"{name}.user", "Str0ngPassw0rd!")
    membership = FamilyMembership(
        family_group_id=family_id, account_id=account.id,
        relationship="unknown", status="active", joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.commit()
    if role:
        await _grant_family_role(db, membership.id, role)
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": f"{name}.user", "password": "Str0ngPassw0rd!", "device_id": f"d-{name}"},
    )
    assert resp.status_code == 200, resp.text
    return membership.id, {"Authorization": f"Bearer {resp.json()['access_token']}"}


# --- Wagle naming migration ----------------------------------------------


async def test_database_carries_no_historical_identifier(db):
    """Migration 0007's result, asserted against the live catalog."""
    for query in (
        f"SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename LIKE '%{HISTORICAL}%'",
        f"SELECT count(*) FROM pg_indexes WHERE schemaname='public' AND indexname LIKE '%{HISTORICAL}%'",
        f"SELECT count(*) FROM pg_constraint WHERE conname LIKE '%{HISTORICAL}%'",
        f"SELECT count(*) FROM pg_proc WHERE proname LIKE '%{HISTORICAL}%'",
        f"SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgname LIKE '%{HISTORICAL}%'",
        f"SELECT count(*) FROM permissions WHERE code LIKE '{HISTORICAL}%'",
        f"SELECT count(*) FROM roles WHERE service_code = '{HISTORICAL}'",
    ):
        assert (await db.execute(text(query))).scalar_one() == 0, query


# The tables migration `0007` renamed out of the historical `doran` namespace.
# MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001 replaced a `count(*) == 7`
# assertion with this explicit set. The count was not wrong, it was fragile and
# weaker: any seven `wagle%` tables satisfied it, and it failed the moment the
# domain legitimately grew (Wave 3 added three). Naming them proves the actual
# claim — that each renamed table exists — and keeps proving it as the domain
# grows.
RENAMED_WAGLE_TABLES = {
    "wagle_rooms",
    "wagle_direct_pairs",
    "wagle_participants",
    "wagle_messages",
    "wagle_participant_read_states",
    "wagle_service_bindings",
    "wagle_service_audit_log",
}


async def test_wagle_objects_and_role_bindings_survived_the_rename(db):
    present = {
        row
        for row in (
            await db.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname='public' AND tablename LIKE 'wagle%'"
                )
            )
        ).scalars()
    }
    perms = (
        await db.execute(text("SELECT count(*) FROM permissions WHERE code LIKE 'wagle%'"))
    ).scalar_one()
    bound = (
        await db.execute(
            text(
                "SELECT count(*) FROM role_permissions rp "
                "JOIN permissions p ON p.id = rp.permission_id WHERE p.code LIKE 'wagle%'"
            )
        )
    ).scalar_one()
    missing = RENAMED_WAGLE_TABLES - present
    assert not missing, f"migration 0007 left these tables un-renamed: {sorted(missing)}"
    assert perms == 5
    assert bound > 0, "renaming a permission code must not orphan its role bindings"


async def test_historical_route_prefix_is_gone_and_wagle_answers(client, family_env):
    """The old prefix must not be served in parallel with the new one."""
    family_id = family_env["family_id"]
    headers = family_env["admin"].headers

    old = await client.get(f"/api/families/{family_id}/{HISTORICAL}/rooms", headers=headers)
    new = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=headers)

    assert old.status_code == 404
    assert new.status_code == 200


async def test_openapi_exposes_only_the_wagle_prefix(client):
    schema = (await client.get("/openapi.json")).json()
    historical_paths = [p for p in schema["paths"] if HISTORICAL in p]
    wagle_paths = [p for p in schema["paths"] if "/wagle/" in p]
    assert historical_paths == []
    assert wagle_paths, "the Wagle routes must be published"


# --- Markpoint activation lifecycle --------------------------------------


async def test_member_requests_and_admin_approves_activation(db, client):
    family_id = await create_family(db, "Requesting")
    member_id, member_h = await _account_login(client, db, family_id, "mreq")
    _admin_id, admin_h = await _account_login(client, db, family_id, "madmin", role="admin")

    created = await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=member_h)
    assert created.status_code == 201, created.text
    assert created.json()["status"] == "PENDING"
    assert created.json()["requester_membership_id"] == member_id

    request_id = created.json()["id"]
    approved = await client.post(
        f"/api/families/{family_id}/markpoint/activation-requests/{request_id}/approve",
        json={"decision_note": "ok"}, headers=admin_h,
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "APPROVED"
    assert approved.json()["processed_at"] is not None

    # The service is now active, and the requester gained no admin role from it.
    access = await client.get(f"/api/families/{family_id}/markpoint/access", headers=member_h)
    assert access.json()["subscription_status"] == "active"
    assert access.json()["has_default_access"] is True
    assert access.json()["is_service_admin"] is False


async def test_admin_can_reject_and_the_service_stays_inactive(db, client):
    family_id = await create_family(db, "Rejecting")
    _member_id, member_h = await _account_login(client, db, family_id, "rreq")
    _admin_id, admin_h = await _account_login(client, db, family_id, "radmin", role="admin")

    request_id = (
        await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=member_h)
    ).json()["id"]
    rejected = await client.post(
        f"/api/families/{family_id}/markpoint/activation-requests/{request_id}/reject",
        json={"decision_note": "not now"}, headers=admin_h,
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "REJECTED"

    access = await client.get(f"/api/families/{family_id}/markpoint/access", headers=member_h)
    assert access.json()["subscription_status"] != "active"
    assert access.json()["has_default_access"] is False


async def test_a_processed_request_cannot_be_processed_again(db, client):
    family_id = await create_family(db, "Twice")
    _m, member_h = await _account_login(client, db, family_id, "treq")
    _a, admin_h = await _account_login(client, db, family_id, "tadmin", role="admin")

    request_id = (
        await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=member_h)
    ).json()["id"]
    first = await client.post(
        f"/api/families/{family_id}/markpoint/activation-requests/{request_id}/approve",
        json={}, headers=admin_h,
    )
    assert first.status_code == 200

    again = await client.post(
        f"/api/families/{family_id}/markpoint/activation-requests/{request_id}/reject",
        json={}, headers=admin_h,
    )
    assert again.status_code == 409


async def test_only_one_pending_request_per_family(db, client):
    family_id = await create_family(db, "OnePending")
    _m1, first_h = await _account_login(client, db, family_id, "pend1")
    _m2, second_h = await _account_login(client, db, family_id, "pend2")

    assert (
        await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=first_h)
    ).status_code == 201
    # A different member cannot open a competing request...
    clash = await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=second_h)
    assert clash.status_code == 409
    # ...but the original requester asking again is idempotent, not an error.
    repeat = await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=first_h)
    assert repeat.status_code == 201


async def test_a_plain_member_cannot_approve(db, client):
    family_id = await create_family(db, "NoApprove")
    _m, member_h = await _account_login(client, db, family_id, "napp")
    request_id = (
        await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=member_h)
    ).json()["id"]

    denied = await client.post(
        f"/api/families/{family_id}/markpoint/activation-requests/{request_id}/approve",
        json={}, headers=member_h,
    )
    assert denied.status_code == 403


async def test_cross_family_approval_is_denied(db, client):
    family_a = await create_family(db, "A")
    family_b = await create_family(db, "B")
    _m, member_h = await _account_login(client, db, family_a, "xreq")
    _a, admin_b_h = await _account_login(client, db, family_b, "xadmin", role="admin")

    request_id = (
        await client.post(f"/api/families/{family_a}/markpoint/activation-requests", headers=member_h)
    ).json()["id"]

    # Family B's admin has no authority in family A ...
    assert (
        await client.post(
            f"/api/families/{family_a}/markpoint/activation-requests/{request_id}/approve",
            json={}, headers=admin_b_h,
        )
    ).status_code == 403
    # ... and cannot reach A's request through B's own path either.
    assert (
        await client.post(
            f"/api/families/{family_b}/markpoint/activation-requests/{request_id}/approve",
            json={}, headers=admin_b_h,
        )
    ).status_code == 404


async def test_requesting_an_already_active_service_is_a_conflict(db, client):
    family_id = await create_family(db, "AlreadyOn")
    _m, member_h = await _account_login(client, db, family_id, "aoreq")
    _a, admin_h = await _account_login(client, db, family_id, "aoadmin", role="admin")
    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=admin_h)

    resp = await client.post(f"/api/families/{family_id}/markpoint/activation-requests", headers=member_h)
    assert resp.status_code == 409


async def test_direct_activation_is_idempotent_and_grants_no_role(db, client):
    family_id = await create_family(db, "Direct")
    admin_membership_id, admin_h = await _account_login(client, db, family_id, "dadmin", role="admin")

    first = await client.post(f"/api/families/{family_id}/markpoint/activate", headers=admin_h)
    second = await client.post(f"/api/families/{family_id}/markpoint/activate", headers=admin_h)
    assert first.status_code == second.status_code == 200
    assert second.json()["status"] == "active"

    access = await client.get(f"/api/families/{family_id}/markpoint/access", headers=admin_h)
    assert access.json()["is_service_admin"] is False, "activating must not grant ServiceAdmin"
    assert admin_membership_id


# --- Individual restriction ----------------------------------------------


async def test_restriction_removes_default_access_and_restore_returns_it(db, client):
    family_id = await create_family(db, "Restricting")
    target_id, target_h = await _account_login(client, db, family_id, "rtarget")
    _a, admin_h = await _account_login(client, db, family_id, "radmin2", role="admin")
    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=admin_h)

    before = await client.get(f"/api/families/{family_id}/markpoint/access", headers=target_h)
    assert before.json()["has_default_access"] is True

    restricted = await client.post(
        f"/api/families/{family_id}/markpoint/restrictions",
        json={"target_membership_id": target_id, "reason": "temporary"}, headers=admin_h,
    )
    assert restricted.status_code == 201, restricted.text

    during = await client.get(f"/api/families/{family_id}/markpoint/access", headers=target_h)
    assert during.json()["has_default_access"] is False
    assert during.json()["is_restricted"] is True
    assert during.json()["restriction_reason"] == "temporary"

    restored = await client.delete(
        f"/api/families/{family_id}/markpoint/restrictions/{target_id}", headers=admin_h
    )
    assert restored.status_code == 200
    assert restored.json()["status"] == "RESTORED"
    assert restored.json()["restored_at"] is not None

    after = await client.get(f"/api/families/{family_id}/markpoint/access", headers=target_h)
    assert after.json()["has_default_access"] is True
    assert after.json()["is_restricted"] is False


async def test_restriction_is_idempotent_and_keeps_history(db, client):
    family_id = await create_family(db, "IdemRestrict")
    target_id, _t = await _account_login(client, db, family_id, "itarget")
    _a, admin_h = await _account_login(client, db, family_id, "iadmin", role="admin")

    first = await client.post(
        f"/api/families/{family_id}/markpoint/restrictions",
        json={"target_membership_id": target_id}, headers=admin_h,
    )
    second = await client.post(
        f"/api/families/{family_id}/markpoint/restrictions",
        json={"target_membership_id": target_id}, headers=admin_h,
    )
    assert first.json()["id"] == second.json()["id"], "must not stack duplicate restrictions"

    rows = (
        await db.execute(
            select(MarkpointAccessRestriction).where(
                MarkpointAccessRestriction.target_membership_id == target_id
            )
        )
    ).scalars().all()
    assert len(rows) == 1


async def test_restore_without_an_active_restriction_is_not_found(db, client):
    family_id = await create_family(db, "NoRestriction")
    target_id, _t = await _account_login(client, db, family_id, "ntarget")
    _a, admin_h = await _account_login(client, db, family_id, "nadmin", role="admin")

    resp = await client.delete(
        f"/api/families/{family_id}/markpoint/restrictions/{target_id}", headers=admin_h
    )
    assert resp.status_code == 404


async def test_a_plain_member_cannot_restrict_anyone(db, client):
    family_id = await create_family(db, "MemberRestrict")
    target_id, _t = await _account_login(client, db, family_id, "mrtarget")
    _m, member_h = await _account_login(client, db, family_id, "mrmember")

    resp = await client.post(
        f"/api/families/{family_id}/markpoint/restrictions",
        json={"target_membership_id": target_id}, headers=member_h,
    )
    assert resp.status_code == 403


async def test_cross_family_restriction_is_denied(db, client):
    family_a = await create_family(db, "RA")
    family_b = await create_family(db, "RB")
    outsider_id, _o = await _account_login(client, db, family_b, "outsider")
    _a, admin_a_h = await _account_login(client, db, family_a, "raadmin", role="admin")

    resp = await client.post(
        f"/api/families/{family_a}/markpoint/restrictions",
        json={"target_membership_id": outsider_id}, headers=admin_a_h,
    )
    assert resp.status_code == 404


async def test_restriction_does_not_create_any_participation_record(db, client):
    """D5-B: access control is not Mission participation."""
    family_id = await create_family(db, "NoParticipation")
    target_id, _t = await _account_login(client, db, family_id, "ptarget")
    _a, admin_h = await _account_login(client, db, family_id, "padmin", role="admin")
    await client.post(f"/api/families/{family_id}/markpoint/activate", headers=admin_h)
    await client.post(
        f"/api/families/{family_id}/markpoint/restrictions",
        json={"target_membership_id": target_id}, headers=admin_h,
    )

    tables = (
        await db.execute(
            text(
                "SELECT count(*) FROM pg_tables WHERE schemaname='public' "
                "AND tablename LIKE '%participant%' AND tablename LIKE 'markpoint%'"
            )
        )
    ).scalar_one()
    assert tables == 0, "no MarkpointParticipant aggregate may exist"
    assert (await db.execute(text("SELECT count(*) FROM missions"))).scalar_one() == 0


# --- Markpoint -> Wagle system event relay -------------------------------


async def _relay_env(db, family_env):
    principal_actor = await create_service_actor(
        db, family_env["family_id"], service_code="markpoint", name="markpoint-service"
    )
    from app.domains.wagle.models import ServicePrincipal

    principal = await db.get(ServicePrincipal, principal_actor.principal_id)
    return principal_actor, principal


def _envelope(family_id, principal_id, binding_id, *, source_event_id="evt-1"):
    return MarkpointSystemEventEnvelope(
        source_event_id=source_event_id,
        event_type="mission_approved",
        family_group_id=family_id,
        service_principal_id=principal_id,
        approved_room_binding_id=binding_id,
        occurred_at=datetime.now(timezone.utc),
        payload={"mission_title": "reading"},
    )


async def test_relay_publishes_a_system_message_under_the_service_principal(db, family_env):
    actor, principal = await _relay_env(db, family_env)
    adapter = WagleMarkpointSystemEventAdapter(db, principal)

    result = await adapter.publish(
        _envelope(family_env["family_id"], principal.id, actor.binding_id)
    )
    assert result.deduplicated is False

    row = (
        await db.execute(
            text(
                "SELECT message_type, service_principal_id, sender_participant_id, source "
                "FROM wagle_messages WHERE source_event_id = 'evt-1'"
            )
        )
    ).mappings().one()
    assert row["message_type"] == "SERVICE_ACTION"
    assert row["service_principal_id"] == principal.id
    assert row["sender_participant_id"] is None, "a service must never post as a human"
    assert row["source"] == "markpoint"


async def test_relay_deduplicates_the_same_source_event(db, family_env):
    actor, principal = await _relay_env(db, family_env)
    adapter = WagleMarkpointSystemEventAdapter(db, principal)
    envelope = _envelope(family_env["family_id"], principal.id, actor.binding_id, source_event_id="evt-dup")

    first = await adapter.publish(envelope)
    second = await adapter.publish(envelope)

    assert first.deduplicated is False
    assert second.deduplicated is True
    count = (
        await db.execute(
            text("SELECT count(*) FROM wagle_messages WHERE source_event_id = 'evt-dup'")
        )
    ).scalar_one()
    assert count == 1


async def test_relay_rejects_an_unapproved_room_binding(db, family_env):
    _actor, principal = await _relay_env(db, family_env)
    adapter = WagleMarkpointSystemEventAdapter(db, principal)

    with pytest.raises(MarkpointSystemEventEnvelopeError):
        await adapter.publish(
            _envelope(family_env["family_id"], principal.id, binding_id=999_999)
        )


async def test_relay_rejects_a_binding_from_another_family(db, family_env):
    actor, principal = await _relay_env(db, family_env)
    other_family = await create_family(db, "RelayOther")
    adapter = WagleMarkpointSystemEventAdapter(db, principal)

    with pytest.raises(MarkpointSystemEventEnvelopeError):
        await adapter.publish(_envelope(other_family, principal.id, actor.binding_id))


async def test_relay_refuses_an_envelope_naming_a_different_principal(db, family_env):
    actor, principal = await _relay_env(db, family_env)
    adapter = WagleMarkpointSystemEventAdapter(db, principal)

    with pytest.raises(ValueError):
        await adapter.publish(
            _envelope(family_env["family_id"], principal.id + 1, actor.binding_id)
        )


async def test_envelope_requires_a_service_actor_and_binding():
    """The port refuses a malformed envelope before any adapter sees it."""
    for bad in (
        {"service_principal_id": 0},
        {"approved_room_binding_id": 0},
        {"family_group_id": 0},
        {"source_event_id": ""},
    ):
        kwargs = {
            "source_event_id": "e", "event_type": "t", "family_group_id": 1,
            "service_principal_id": 1, "approved_room_binding_id": 1,
            "occurred_at": datetime.now(timezone.utc), "payload": {},
        }
        kwargs.update(bad)
        with pytest.raises(MarkpointSystemEventEnvelopeError):
            MarkpointSystemEventEnvelope(**kwargs)


async def test_markpoint_domain_never_imports_a_wagle_table(db):
    """The cross-domain boundary, asserted against the source itself."""
    import pathlib

    domain = pathlib.Path("app/domains/markpoint_access")
    offenders = []
    for path in domain.rglob("*.py"):
        text_body = path.read_text()
        if "wagle.models" in text_body or "from app.domains.wagle.models" in text_body:
            offenders.append(str(path))
    assert offenders == [], f"Markpoint must reach Wagle through its service, not its tables: {offenders}"
