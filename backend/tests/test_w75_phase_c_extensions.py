"""W7.5 Phase C — additive profile self-service and mission detail fields.

Covers: `PATCH /api/me` (2z), `PATCH /api/families/{family_id}/members/me`
(self-service relationship, 1f/2z), `MissionOut.description/checklist/
rejection_reason/reviewer_display_name` and the checklist toggle endpoint
(1k/1s). Every fixture is synthetic, created inside the isolated Phase 2 test
database.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import text

from app.domains.family import auth_service
from app.domains.family.models import Account, FamilyGroup, FamilyMembership, ServiceSubscription
from app.domains.markpoint_target import service as markpoint_service

PASSWORD = "Str0ngPassw0rd!"


async def _actor(db, client, family_id: int, name: str) -> dict:
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family_id,
        account_id=account.id,
        relationship="unknown",
        status="active",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.flush()
    await auth_service.create_credential(db, account.id, f"{name}.{family_id}", PASSWORD)
    await db.commit()

    resp = await client.post(
        "/api/auth/account/login",
        json={"username": f"{name}.{family_id}", "password": PASSWORD, "device_id": f"d-{name}"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"account": account, "membership": membership, "headers": {"Authorization": f"Bearer {token}"}}


async def _family(db, name: str) -> FamilyGroup:
    family = FamilyGroup(name=name, status="active")
    db.add(family)
    await db.flush()
    return family


# --- PATCH /api/me (2z self-service profile edit) --------------------------


@pytest.mark.asyncio
async def test_patch_me_updates_profile_fields_and_get_me_reflects_them(db, client):
    family = await _family(db, "profile-family")
    actor = await _actor(db, client, family.id, "owner")

    patch = await client.patch(
        "/api/me",
        json={"display_name": "새이름", "bio": "안녕하세요", "birthday": "2015-04-12", "avatar_color": "#5A35DF"},
        headers=actor["headers"],
    )
    assert patch.status_code == 200, patch.text
    body = patch.json()
    assert body["display_name"] == "새이름"
    assert body["bio"] == "안녕하세요"
    assert body["birthday"] == "2015-04-12"
    assert body["avatar_color"] == "#5A35DF"

    fresh = await client.get("/api/me", headers=actor["headers"])
    assert fresh.status_code == 200
    assert fresh.json()["display_name"] == "새이름"
    assert fresh.json()["bio"] == "안녕하세요"


@pytest.mark.asyncio
async def test_patch_me_partial_update_leaves_other_fields_untouched(db, client):
    family = await _family(db, "profile-family-2")
    actor = await _actor(db, client, family.id, "owner")
    await client.patch("/api/me", json={"bio": "first"}, headers=actor["headers"])

    resp = await client.patch("/api/me", json={"birthday": "2016-01-01"}, headers=actor["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["bio"] == "first"
    assert body["birthday"] == "2016-01-01"


@pytest.mark.asyncio
async def test_patch_me_rejects_invalid_avatar_color(db, client):
    family = await _family(db, "profile-family-3")
    actor = await _actor(db, client, family.id, "owner")
    resp = await client.patch("/api/me", json={"avatar_color": "not-a-hex-color"}, headers=actor["headers"])
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_me_returns_joined_at_per_family(db, client):
    family = await _family(db, "joined-at-family")
    actor = await _actor(db, client, family.id, "owner")
    me = await client.get("/api/me", headers=actor["headers"])
    assert me.status_code == 200
    entry = next(f for f in me.json()["authorized_families"] if f["family_group_id"] == family.id)
    assert entry["joined_at"] is not None


# --- PATCH /api/families/{family_id}/members/me (self-service relationship) -


@pytest.mark.asyncio
async def test_self_service_relationship_update_requires_no_manage_permission(db, client):
    family = await _family(db, "role-family")
    actor = await _actor(db, client, family.id, "child-actor")  # no roles granted at all

    resp = await client.patch(
        f"/api/families/{family.id}/members/me",
        json={"relationship": "child"},
        headers=actor["headers"],
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["relationship"] == "child"

    me = await client.get("/api/me", headers=actor["headers"])
    entry = next(f for f in me.json()["authorized_families"] if f["family_group_id"] == family.id)
    assert entry["relationship"] == "child"


@pytest.mark.asyncio
async def test_self_service_relationship_update_rejects_unknown_code(db, client):
    family = await _family(db, "role-family-2")
    actor = await _actor(db, client, family.id, "actor")
    resp = await client.patch(
        f"/api/families/{family.id}/members/me",
        json={"relationship": "not-a-real-relationship"},
        headers=actor["headers"],
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_self_service_relationship_update_rejects_non_member_family(db, client):
    family = await _family(db, "role-family-3")
    other = await _family(db, "role-family-4")
    actor = await _actor(db, client, family.id, "actor")
    resp = await client.patch(
        f"/api/families/{other.id}/members/me",
        json={"relationship": "child"},
        headers=actor["headers"],
    )
    assert resp.status_code == 403


# --- Mission description/checklist/rejection_reason/reviewer name (1k/1s) --


async def _mission_env(db):
    family = FamilyGroup(name="mission-family", status="active")
    db.add(family)
    await db.flush()
    db.add(ServiceSubscription(family_group_id=family.id, service_code="markpoint", status="active", started_at=datetime.now(timezone.utc)))
    await db.flush()
    manager_account = Account(display_name="관리자", status="active")
    child_account = Account(display_name="아이", status="active")
    db.add_all([manager_account, child_account])
    await db.flush()
    manager = FamilyMembership(family_group_id=family.id, account_id=manager_account.id, relationship="unknown", status="active", joined_at=datetime.now(timezone.utc))
    child = FamilyMembership(family_group_id=family.id, account_id=child_account.id, relationship="unknown", status="active", joined_at=datetime.now(timezone.utc))
    db.add_all([manager, child])
    await db.flush()
    role_id = (await db.execute(text("SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='markpoint' AND code='mission_manager'"))).scalar_one()
    from app.domains.family.models import MembershipRoleAssignment
    db.add(MembershipRoleAssignment(membership_id=manager.id, role_id=role_id))
    await db.commit()
    return family, manager, child


@pytest.mark.asyncio
async def test_mission_out_exposes_description_and_checklist(db):
    family, manager, child = await _mission_env(db)
    mission = await markpoint_service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=date.today(), reward_amount=10,
        description="오늘의 숙제를 모두 완료해요", checklist=["수학 익힘책 12쪽", "일기 쓰기"],
    )
    out = await markpoint_service.mission_out(db, mission)
    assert out.description == "오늘의 숙제를 모두 완료해요"
    assert [item.label for item in out.checklist] == ["수학 익힘책 12쪽", "일기 쓰기"]
    assert all(item.done is False for item in out.checklist)
    assert out.rejection_reason is None
    assert out.reviewer_display_name is None


@pytest.mark.asyncio
async def test_reject_mission_exposes_reason_and_reviewer_name(db):
    family, manager, child = await _mission_env(db)
    mission = await markpoint_service.create_mission(db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=date.today(), reward_amount=10)
    await markpoint_service.submit_mission(db, family.id, child, mission.id)
    mission = await markpoint_service.reject_mission(db, family.id, manager, mission.id, "다시 찍어줘")
    out = await markpoint_service.mission_out(db, mission)
    assert out.rejection_reason == "다시 찍어줘"
    assert out.reviewer_display_name == "관리자"


@pytest.mark.asyncio
async def test_update_mission_checklist_toggles_by_assignee(db):
    family, manager, child = await _mission_env(db)
    mission = await markpoint_service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=date.today(), reward_amount=10,
        checklist=["a", "b"],
    )
    updated = await markpoint_service.update_mission_checklist(
        db, family.id, child, mission.id, [{"label": "a", "done": True}, {"label": "b", "done": False}],
    )
    assert [item["done"] for item in updated.checklist] == [True, False]
    # Label is server-controlled, never taken from the caller's payload.
    assert [item["label"] for item in updated.checklist] == ["a", "b"]


@pytest.mark.asyncio
async def test_update_mission_checklist_rejects_wrong_assignee(db):
    family, manager, child = await _mission_env(db)
    mission = await markpoint_service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=date.today(), reward_amount=10,
        checklist=["a"],
    )
    with pytest.raises(Exception):
        await markpoint_service.update_mission_checklist(db, family.id, manager, mission.id, [{"label": "a", "done": True}])


@pytest.mark.asyncio
async def test_update_mission_checklist_rejects_after_submission(db):
    family, manager, child = await _mission_env(db)
    mission = await markpoint_service.create_mission(
        db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=date.today(), reward_amount=10,
        checklist=["a"],
    )
    await markpoint_service.submit_mission(db, family.id, child, mission.id)
    with pytest.raises(Exception):
        await markpoint_service.update_mission_checklist(db, family.id, child, mission.id, [{"label": "a", "done": True}])


@pytest.mark.asyncio
async def test_checklist_http_endpoint_round_trips(db, client):
    family = await _family(db, "checklist-http-family")
    db.add(ServiceSubscription(family_group_id=family.id, service_code="markpoint", status="active", started_at=datetime.now(timezone.utc)))
    await db.commit()
    manager = await _actor(db, client, family.id, "manager")
    role_id = (await db.execute(text("SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='markpoint' AND code='mission_manager'"))).scalar_one()
    from app.domains.family.models import MembershipRoleAssignment
    db.add(MembershipRoleAssignment(membership_id=manager["membership"].id, role_id=role_id))
    await db.commit()
    child = await _actor(db, client, family.id, "child")

    created = await client.post(
        f"/api/families/{family.id}/markpoint/missions",
        json={
            "assignee_membership_id": child["membership"].id,
            "title": "숙제",
            "scheduled_for": str(date.today()),
            "reward_amount": 10,
            "checklist": ["수학", "일기"],
        },
        headers=manager["headers"],
    )
    assert created.status_code == 201, created.text
    mission_id = created.json()["id"]
    assert [item["label"] for item in created.json()["checklist"]] == ["수학", "일기"]

    toggled = await client.patch(
        f"/api/families/{family.id}/markpoint/missions/{mission_id}/checklist",
        json={"items": [{"label": "수학", "done": True}, {"label": "일기", "done": False}]},
        headers=child["headers"],
    )
    assert toggled.status_code == 200, toggled.text
    assert toggled.json()["checklist"][0]["done"] is True

    # The manager is not the assignee, so this must not be theirs to toggle.
    denied = await client.patch(
        f"/api/families/{family.id}/markpoint/missions/{mission_id}/checklist",
        json={"items": [{"label": "수학", "done": False}, {"label": "일기", "done": False}]},
        headers=manager["headers"],
    )
    assert denied.status_code == 404


# --- Wagle message reply_to_message_id (2g) ---------------------------------


@pytest.mark.asyncio
async def test_reply_to_message_id_round_trips_through_the_api(family_env):
    client, family_id = family_env["client"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    original = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "m1", "body": "저녁 뭐 먹을까?"},
        headers=admin.headers,
    )
    assert original.status_code == 201
    assert original.json()["reply_to_message_id"] is None
    original_id = original.json()["id"]

    reply = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "m2", "body": "김치찌개 어때요", "reply_to_message_id": original_id},
        headers=member.headers,
    )
    assert reply.status_code == 201, reply.text
    assert reply.json()["reply_to_message_id"] == original_id

    listed = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        headers=admin.headers,
    )
    by_id = {m["id"]: m for m in listed.json()["items"]}
    assert by_id[reply.json()["id"]]["reply_to_message_id"] == original_id


@pytest.mark.asyncio
async def test_reply_to_message_id_rejects_a_message_from_another_room(family_env):
    client, family_id = family_env["client"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_a = (await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "room-a"},
        headers=admin.headers,
    )).json()
    room_b = (await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "room-b"},
        headers=admin.headers,
    )).json()
    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_a['id']}/participants", json={"family_membership_id": member.membership_id, "room_role": "member"}, headers=admin.headers)
    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_b['id']}/participants", json={"family_membership_id": member.membership_id, "room_role": "member"}, headers=admin.headers)

    in_a = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_a['id']}/messages",
        json={"client_message_id": "a1", "body": "room a message"},
        headers=admin.headers,
    )
    assert in_a.status_code == 201

    forged_reply = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_b['id']}/messages",
        json={"client_message_id": "b1", "body": "cross-room reply attempt", "reply_to_message_id": in_a.json()["id"]},
        headers=admin.headers,
    )
    assert forged_reply.status_code == 404
