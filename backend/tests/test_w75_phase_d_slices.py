"""W7.5 Phase D — new vertical Slices. One section per Slice, added as each
lands (see engineering/phase2/MONGLE_W7_5_PHASE_D_SLICE_MAPPING.md for the
full execution order). Every fixture here is synthetic, created inside the
isolated Phase 2 test database.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from sqlalchemy import text

from app.domains.family.models import Account, FamilyGroup, FamilyMembership, MembershipRoleAssignment, ServiceSubscription
from app.domains.family_todo import service as todo_service
from app.domains.family_rules import service as rules_service
from app.domains.notification_preferences import service as prefs_service
from app.domains.notification_preferences.schemas import DEFAULTS
from app.domains.family_schedule import service as schedule_service
from app.domains.family_album import service as album_service
from app.domains.reward_catalog import service as reward_service
from app.domains.markpoint_target import service as markpoint_service
from app.domains.account_notification import service as notification_service
from app.domains.account_notification.models import AccountNotification
from app.domains.family_activity_log import service as activity_log_service
from app.domains.family_search import service as search_service


async def _family_with_two_members(db):
    family = FamilyGroup(name="todo-family", status="active")
    db.add(family)
    await db.flush()
    a1 = Account(display_name="Parent", status="active")
    a2 = Account(display_name="Child", status="active")
    db.add_all([a1, a2])
    await db.flush()
    m1 = FamilyMembership(family_group_id=family.id, account_id=a1.id, relationship="mother", status="active", joined_at=datetime.now(timezone.utc))
    m2 = FamilyMembership(family_group_id=family.id, account_id=a2.id, relationship="child", status="active", joined_at=datetime.now(timezone.utc))
    db.add_all([m1, m2])
    await db.commit()
    return family, m1, m2


# --- SLICE-TODO (1i) --------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_list_todo(db):
    family, parent, child = await _family_with_two_members(db)
    todo = await todo_service.create_todo(db, family.id, parent, title="방 청소하기", assignee_membership_id=child.id, due_at=None)
    assert todo.status == "open"
    listed = await todo_service.list_todos(db, family.id)
    assert [t.id for t in listed] == [todo.id]


@pytest.mark.asyncio
async def test_toggle_todo_sets_completed_at(db):
    family, parent, child = await _family_with_two_members(db)
    todo = await todo_service.create_todo(db, family.id, parent, title="숙제", assignee_membership_id=child.id, due_at=None)
    done = await todo_service.update_todo(db, family.id, todo.id, title=None, assignee_membership_id=None, due_at=None, status_value="done")
    assert done.status == "done"
    assert done.completed_at is not None
    reopened = await todo_service.update_todo(db, family.id, todo.id, title=None, assignee_membership_id=None, due_at=None, status_value="open")
    assert reopened.completed_at is None


@pytest.mark.asyncio
async def test_todo_assignee_must_be_active_member_of_same_family(db):
    family, parent, child = await _family_with_two_members(db)
    other_family = FamilyGroup(name="other", status="active")
    db.add(other_family)
    await db.flush()
    other_account = Account(display_name="Outsider", status="active")
    db.add(other_account)
    await db.flush()
    outsider = FamilyMembership(family_group_id=other_family.id, account_id=other_account.id, relationship="unknown", status="active", joined_at=datetime.now(timezone.utc))
    db.add(outsider)
    await db.commit()

    with pytest.raises(Exception):
        await todo_service.create_todo(db, family.id, parent, title="x", assignee_membership_id=outsider.id, due_at=None)


@pytest.mark.asyncio
async def test_todo_http_create_toggle_delete_round_trip(db, client):
    family, parent_m, child_m = await _family_with_two_members(db)
    # Real HTTP auth: log in as the parent Account.
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent_m.account_id, "todo.parent", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "todo.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = await client.post(f"/api/families/{family.id}/todos", json={"title": "장보기", "assignee_membership_id": child_m.id, "due_at": None}, headers=headers)
    assert created.status_code == 201, created.text
    todo_id = created.json()["id"]

    listed = await client.get(f"/api/families/{family.id}/todos", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    toggled = await client.patch(f"/api/families/{family.id}/todos/{todo_id}", json={"status": "done"}, headers=headers)
    assert toggled.status_code == 200
    assert toggled.json()["status"] == "done"

    deleted = await client.delete(f"/api/families/{family.id}/todos/{todo_id}", headers=headers)
    assert deleted.status_code == 204

    empty = await client.get(f"/api/families/{family.id}/todos", headers=headers)
    assert empty.json() == []


# --- SLICE-FAMILY-RULES (1v) -------------------------------------------------


async def _grant_family_owner_role(db, membership_id: int) -> None:
    role_id = (await db.execute(text("SELECT id FROM roles WHERE scope_type='FAMILY' AND code='owner'"))).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=membership_id, role_id=role_id))
    await db.commit()


@pytest.mark.asyncio
async def test_replace_rules_is_whole_list_and_ordered(db):
    family, parent, child = await _family_with_two_members(db)
    await _grant_family_owner_role(db, parent.id)
    entries = [
        {"category": "life", "label": "취침 시간", "value_text": "오후 10:00"},
        {"category": "point", "label": "보상 교환", "value_text": "보호자 승인 필요"},
    ]
    result = await rules_service.replace_rules(db, family.id, parent, entries)
    assert [(r.category, r.label, r.sort_order) for r in result] == [("life", "취침 시간", 0), ("point", "보상 교환", 1)]

    # Replacing again drops the old rows entirely rather than appending.
    result2 = await rules_service.replace_rules(db, family.id, parent, [{"category": "life", "label": "새 규칙", "value_text": "x"}])
    listed = await rules_service.list_rules(db, family.id)
    assert len(listed) == 1
    assert listed[0].label == "새 규칙"


@pytest.mark.asyncio
async def test_replace_rules_http_requires_family_members_manage(db, client):
    family, parent, child = await _family_with_two_members(db)
    await _grant_family_owner_role(db, parent.id)
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent.account_id, "rules.parent", "Str0ngPassw0rd!")
    await auth_service.create_credential(db, child.account_id, "rules.child", "Str0ngPassw0rd!")
    await db.commit()

    parent_login = await client.post("/api/auth/account/login", json={"username": "rules.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    child_login = await client.post("/api/auth/account/login", json={"username": "rules.child", "password": "Str0ngPassw0rd!", "device_id": "d2"})
    parent_headers = {"Authorization": f"Bearer {parent_login.json()['access_token']}"}
    child_headers = {"Authorization": f"Bearer {child_login.json()['access_token']}"}

    denied = await client.put(f"/api/families/{family.id}/rules", json={"rules": [{"category": "life", "label": "x", "value_text": "y"}]}, headers=child_headers)
    assert denied.status_code == 403

    allowed = await client.put(f"/api/families/{family.id}/rules", json={"rules": [{"category": "life", "label": "x", "value_text": "y"}]}, headers=parent_headers)
    assert allowed.status_code == 200

    read_as_child = await client.get(f"/api/families/{family.id}/rules", headers=child_headers)
    assert read_as_child.status_code == 200
    assert len(read_as_child.json()) == 1


# --- SLICE-NOTIFICATION-PREFERENCES (2n) ------------------------------------


@pytest.mark.asyncio
async def test_notification_preferences_default_before_any_write(db):
    family, parent, child = await _family_with_two_members(db)
    prefs = await prefs_service.get_preferences(db, parent.account_id)
    assert prefs == DEFAULTS


@pytest.mark.asyncio
async def test_notification_preferences_partial_update_preserves_other_keys(db):
    family, parent, child = await _family_with_two_members(db)
    await prefs_service.set_preferences(db, parent.account_id, {"levelup_badge": True})
    updated = await prefs_service.get_preferences(db, parent.account_id)
    assert updated["levelup_badge"] is True
    assert updated["mission_decision"] == DEFAULTS["mission_decision"]

    # A second account's preferences must never leak into or be affected by this.
    other_prefs = await prefs_service.get_preferences(db, child.account_id)
    assert other_prefs == DEFAULTS


@pytest.mark.asyncio
async def test_notification_preferences_http_round_trip(db, client):
    family, parent, child = await _family_with_two_members(db)
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent.account_id, "prefs.parent", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "prefs.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    initial = await client.get("/api/me/notification-preferences", headers=headers)
    assert initial.status_code == 200
    assert {p["pref_key"]: p["enabled"] for p in initial.json()} == DEFAULTS

    updated = await client.put(
        "/api/me/notification-preferences",
        json={"preferences": [{"pref_key": "album_new_photo", "enabled": True}, {"pref_key": "quiet_hours", "enabled": False}]},
        headers=headers,
    )
    assert updated.status_code == 200
    by_key = {p["pref_key"]: p["enabled"] for p in updated.json()}
    assert by_key["album_new_photo"] is True
    assert by_key["quiet_hours"] is False
    assert by_key["mission_decision"] == DEFAULTS["mission_decision"]


# --- SLICE-SCHEDULE (1g/1o/2u) -----------------------------------------------


@pytest.mark.asyncio
async def test_create_and_list_schedule_event_ordered_by_start(db):
    family, parent, child = await _family_with_two_members(db)
    now = datetime.now(timezone.utc)
    later = await schedule_service.create_event(db, family.id, parent, title="여행", starts_at=now + timedelta(days=2), location=None, memo=None, attendee_membership_ids=None, visibility="family")
    sooner = await schedule_service.create_event(db, family.id, child, title="학원", starts_at=now + timedelta(hours=1), location="학원", memo=None, attendee_membership_ids=[child.id], visibility="family")
    listed = await schedule_service.list_events(db, family.id)
    assert [e.id for e in listed] == [sooner.id, later.id]


@pytest.mark.asyncio
async def test_schedule_event_attendees_must_be_active_family_members(db):
    family, parent, child = await _family_with_two_members(db)
    with pytest.raises(Exception):
        await schedule_service.create_event(db, family.id, parent, title="x", starts_at=datetime.now(timezone.utc), location=None, memo=None, attendee_membership_ids=[9999], visibility="family")


@pytest.mark.asyncio
async def test_update_and_delete_schedule_event(db):
    family, parent, child = await _family_with_two_members(db)
    event = await schedule_service.create_event(db, family.id, parent, title="원래 제목", starts_at=datetime.now(timezone.utc), location=None, memo=None, attendee_membership_ids=None, visibility="family")
    updated = await schedule_service.update_event(db, family.id, event.id, {"title": "새 제목", "location": "집"})
    assert updated.title == "새 제목"
    assert updated.location == "집"
    await schedule_service.delete_event(db, family.id, event.id)
    assert await schedule_service.list_events(db, family.id) == []


@pytest.mark.asyncio
async def test_schedule_event_http_round_trip(db, client):
    family, parent, child = await _family_with_two_members(db)
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent.account_id, "sched.parent", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "sched.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = await client.post(
        f"/api/families/{family.id}/schedule-events",
        json={"title": "가족 저녁", "starts_at": datetime.now(timezone.utc).isoformat(), "location": "집", "memo": "삼겹살", "attendee_membership_ids": [child.id]},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    fetched = await client.get(f"/api/families/{family.id}/schedule-events/{event_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["attendee_membership_ids"] == [child.id]

    deleted = await client.delete(f"/api/families/{family.id}/schedule-events/{event_id}", headers=headers)
    assert deleted.status_code == 204
    gone = await client.get(f"/api/families/{family.id}/schedule-events/{event_id}", headers=headers)
    assert gone.status_code == 404


# --- SLICE-ALBUM-METADATA (1h/1p/1w/2y) -------------------------------------


@pytest.mark.asyncio
async def test_create_album_and_add_photo_metadata(db):
    family, parent, child = await _family_with_two_members(db)
    album, count = await album_service.create_album(db, family.id, parent, "여름 여행")
    assert count == 0
    photo = await album_service.add_photo(db, family.id, album.id, child, caption="바다에서", taken_at=None)
    assert photo.uploaded_by_membership_id == child.id
    _album, count2 = await album_service.get_album(db, family.id, album.id, parent.id)
    assert count2 == 1


@pytest.mark.asyncio
async def test_album_shared_with_restricts_visibility(db):
    family, parent, child = await _family_with_two_members(db)
    album, _ = await album_service.create_album(db, family.id, parent, "부모 전용")
    await album_service.update_album(db, family.id, album.id, title=None, shared_with_membership_ids=[parent.id])

    visible_to_parent = await album_service.list_albums(db, family.id, parent.id)
    assert any(a.id == album.id for a, _ in visible_to_parent)

    visible_to_child = await album_service.list_albums(db, family.id, child.id)
    assert not any(a.id == album.id for a, _ in visible_to_child)

    with pytest.raises(Exception):
        await album_service.get_album(db, family.id, album.id, child.id)


@pytest.mark.asyncio
async def test_search_photos_by_caption_respects_visibility(db):
    family, parent, child = await _family_with_two_members(db)
    open_album, _ = await album_service.create_album(db, family.id, parent, "공개 앨범")
    restricted_album, _ = await album_service.create_album(db, family.id, parent, "비공개 앨범")
    await album_service.update_album(db, family.id, restricted_album.id, title=None, shared_with_membership_ids=[parent.id])
    await album_service.add_photo(db, family.id, open_album.id, parent, caption="여름 바다", taken_at=None)
    await album_service.add_photo(db, family.id, restricted_album.id, parent, caption="여름 캠핑", taken_at=None)

    results_for_parent = await album_service.search_photos(db, family.id, parent.id, "여름")
    assert len(results_for_parent) == 2

    results_for_child = await album_service.search_photos(db, family.id, child.id, "여름")
    assert [photo.caption for photo, _album in results_for_child] == ["여름 바다"]


@pytest.mark.asyncio
async def test_album_http_round_trip(db, client):
    family, parent, child = await _family_with_two_members(db)
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent.account_id, "album.parent", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "album.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = await client.post(f"/api/families/{family.id}/albums", json={"title": "가족 여행"}, headers=headers)
    assert created.status_code == 201, created.text
    album_id = created.json()["id"]
    assert created.json()["photo_count"] == 0

    photo = await client.post(f"/api/families/{family.id}/albums/{album_id}/photos", json={"caption": "산 정상에서"}, headers=headers)
    assert photo.status_code == 201, photo.text

    listed = await client.get(f"/api/families/{family.id}/albums", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["photo_count"] == 1

    searched = await client.get(f"/api/families/{family.id}/albums/search", params={"q": "산 정상"}, headers=headers)
    assert searched.status_code == 200
    assert len(searched.json()) == 1


# --- SLICE-REWARD-CATALOG (1l/2h/2j) -----------------------------------------


async def _markpoint_family_with_two_members(db):
    """Same shape as `_family_with_two_members` plus an ACTIVE markpoint
    ServiceSubscription and a `mission_manager` role on the parent --
    Reward management reuses the same manager role Missions already use."""
    family, parent, child = await _family_with_two_members(db)
    db.add(ServiceSubscription(family_group_id=family.id, service_code="markpoint", status="active", started_at=datetime.now(timezone.utc)))
    await db.flush()
    role_id = (await db.execute(text("SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='markpoint' AND code='mission_manager'"))).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=parent.id, role_id=role_id))
    await db.commit()
    return family, parent, child


@pytest.mark.asyncio
async def test_create_reward_requires_mission_manage_permission(db):
    family, parent, child = await _markpoint_family_with_two_members(db)
    with pytest.raises(Exception):
        await reward_service.create_reward(db, family.id, child, name="젤리", cost=30)
    reward = await reward_service.create_reward(db, family.id, parent, name="젤리", cost=30)
    assert reward.cost == 30
    assert reward.is_available is True


@pytest.mark.asyncio
async def test_redeem_reward_debits_own_balance_via_self_spend(db):
    family, parent, child = await _markpoint_family_with_two_members(db)
    reward = await reward_service.create_reward(db, family.id, parent, name="게임 30분", cost=80)

    # Seed the child's balance directly via the Ledger's own entry helper,
    # the same shape `adjust_points` uses -- avoids needing POINTS_ADJUST
    # on this actor just to set up the test fixture.
    from app.domains.markpoint_target.models import MarkpointBalanceProjection
    db.add(MarkpointBalanceProjection(family_group_id=family.id, family_membership_id=child.id, current_balance=100, lifetime_earned=100))
    await db.commit()

    redemption = await reward_service.redeem_reward(db, family.id, child, reward.id, "idem-1")
    assert redemption.cost_at_redemption == 80

    balance = await markpoint_service.own_balance(db, family.id, child)
    assert balance.current_balance == 20


@pytest.mark.asyncio
async def test_redeem_reward_rejects_insufficient_balance(db):
    family, parent, child = await _markpoint_family_with_two_members(db)
    reward = await reward_service.create_reward(db, family.id, parent, name="영화관 나들이", cost=300)
    from app.domains.markpoint_target.models import MarkpointBalanceProjection
    db.add(MarkpointBalanceProjection(family_group_id=family.id, family_membership_id=child.id, current_balance=50, lifetime_earned=50))
    await db.commit()

    with pytest.raises(Exception):
        await reward_service.redeem_reward(db, family.id, child, reward.id, "idem-2")


@pytest.mark.asyncio
async def test_redeem_reward_is_idempotent_on_retry(db):
    family, parent, child = await _markpoint_family_with_two_members(db)
    reward = await reward_service.create_reward(db, family.id, parent, name="젤리", cost=30)
    from app.domains.markpoint_target.models import MarkpointBalanceProjection
    db.add(MarkpointBalanceProjection(family_group_id=family.id, family_membership_id=child.id, current_balance=100, lifetime_earned=100))
    await db.commit()

    first = await reward_service.redeem_reward(db, family.id, child, reward.id, "same-key")
    second = await reward_service.redeem_reward(db, family.id, child, reward.id, "same-key")
    assert first.id == second.id

    balance = await markpoint_service.own_balance(db, family.id, child)
    assert balance.current_balance == 70  # debited once, not twice


@pytest.mark.asyncio
async def test_reward_http_round_trip(db, client):
    family, parent, child = await _markpoint_family_with_two_members(db)
    from app.domains.markpoint_target.models import MarkpointBalanceProjection
    db.add(MarkpointBalanceProjection(family_group_id=family.id, family_membership_id=child.id, current_balance=100, lifetime_earned=100))
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent.account_id, "reward.parent", "Str0ngPassw0rd!")
    await auth_service.create_credential(db, child.account_id, "reward.child", "Str0ngPassw0rd!")
    await db.commit()

    parent_login = await client.post("/api/auth/account/login", json={"username": "reward.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    child_login = await client.post("/api/auth/account/login", json={"username": "reward.child", "password": "Str0ngPassw0rd!", "device_id": "d2"})
    parent_headers = {"Authorization": f"Bearer {parent_login.json()['access_token']}"}
    child_headers = {"Authorization": f"Bearer {child_login.json()['access_token']}"}

    created = await client.post(f"/api/families/{family.id}/rewards", json={"name": "캐릭터 노트", "cost": 50}, headers=parent_headers)
    assert created.status_code == 201, created.text
    reward_id = created.json()["id"]

    denied = await client.post(f"/api/families/{family.id}/rewards", json={"name": "불가", "cost": 10}, headers=child_headers)
    assert denied.status_code == 403

    redeemed = await client.post(f"/api/families/{family.id}/rewards/{reward_id}/redeem", json={"idempotency_key": "k1"}, headers=child_headers)
    assert redeemed.status_code == 201, redeemed.text
    assert redeemed.json()["cost_at_redemption"] == 50


# --- SLICE-NOTIFICATION-LIST (1n) -------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_is_self_scoped(db):
    family, parent, child = await _family_with_two_members(db)
    db.add(AccountNotification(account_id=parent.account_id, title="부모 알림", body="x"))
    db.add(AccountNotification(account_id=child.account_id, title="아이 알림", body="y"))
    await db.commit()

    parent_notifications = await notification_service.list_notifications(db, parent.account_id)
    assert [n.title for n in parent_notifications] == ["부모 알림"]
    child_notifications = await notification_service.list_notifications(db, child.account_id)
    assert [n.title for n in child_notifications] == ["아이 알림"]


@pytest.mark.asyncio
async def test_mark_read_is_idempotent_and_scoped_to_owner(db):
    family, parent, child = await _family_with_two_members(db)
    notif = AccountNotification(account_id=parent.account_id, title="알림")
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    with pytest.raises(Exception):
        await notification_service.mark_read(db, child.account_id, notif.id)

    read_once = await notification_service.mark_read(db, parent.account_id, notif.id)
    assert read_once.read_at is not None
    first_read_at = read_once.read_at
    read_again = await notification_service.mark_read(db, parent.account_id, notif.id)
    assert read_again.read_at == first_read_at  # already-read is a no-op, not re-timestamped


@pytest.mark.asyncio
async def test_mark_all_read_only_touches_unread_rows_for_that_account(db):
    family, parent, child = await _family_with_two_members(db)
    db.add_all([
        AccountNotification(account_id=parent.account_id, title="a"),
        AccountNotification(account_id=parent.account_id, title="b"),
        AccountNotification(account_id=child.account_id, title="c"),
    ])
    await db.commit()

    count = await notification_service.mark_all_read(db, parent.account_id)
    assert count == 2
    parent_notifications = await notification_service.list_notifications(db, parent.account_id)
    assert all(n.read_at is not None for n in parent_notifications)
    child_notifications = await notification_service.list_notifications(db, child.account_id)
    assert all(n.read_at is None for n in child_notifications)


@pytest.mark.asyncio
async def test_notification_http_round_trip(db, client):
    family, parent, child = await _family_with_two_members(db)
    from app.domains.family import auth_service
    await auth_service.create_credential(db, parent.account_id, "notif.parent", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "notif.parent", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    db.add(AccountNotification(account_id=parent.account_id, title="테스트 알림", body="본문"))
    await db.commit()

    listed = await client.get("/api/me/notifications", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    notif_id = listed.json()[0]["id"]
    assert listed.json()[0]["read_at"] is None

    marked = await client.post(f"/api/me/notifications/{notif_id}/read", headers=headers)
    assert marked.status_code == 200
    assert marked.json()["read_at"] is not None

    mark_all = await client.post("/api/me/notifications/read-all", headers=headers)
    assert mark_all.status_code == 204


# --- SLICE-FAMILY-ACTIVITY-LOG (2r) -----------------------------------------


@pytest.mark.asyncio
async def test_activity_log_reads_real_markpoint_audit_events(db):
    family, manager, child = await _markpoint_family_with_two_members(db)
    mission = await markpoint_service.create_mission(db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=10)
    await markpoint_service.submit_mission(db, family.id, child, mission.id)
    await markpoint_service.approve_mission(db, family.id, manager, mission.id)

    entries = await activity_log_service.list_activity(db, family.id)
    actions = [e["action"] for e in entries]
    assert "mission.created" in actions
    assert "mission.submitted" in actions
    assert "mission.approved" in actions
    # Newest first.
    assert entries[0]["occurred_at"] >= entries[-1]["occurred_at"]


@pytest.mark.asyncio
async def test_activity_log_resolves_real_actor_display_names(db):
    family, manager, child = await _markpoint_family_with_two_members(db)
    mission = await markpoint_service.create_mission(db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=10)
    entries = await activity_log_service.list_activity(db, family.id)
    created_entry = next(e for e in entries if e["action"] == "mission.created")
    assert created_entry["actor_display_name"] == "Parent"


@pytest.mark.asyncio
async def test_activity_log_is_family_scoped(db):
    family_a, manager_a, child_a = await _markpoint_family_with_two_members(db)
    family_b, manager_b, child_b = await _markpoint_family_with_two_members(db)
    await markpoint_service.create_mission(db, family_a.id, manager_a, assignee_id=child_a.id, title="a", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=5)
    await markpoint_service.create_mission(db, family_b.id, manager_b, assignee_id=child_b.id, title="b", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=5)

    entries_a = await activity_log_service.list_activity(db, family_a.id)
    assert all(e["payload"] for e in entries_a)  # sanity: real rows, not empty stubs
    assert len(await activity_log_service.list_activity(db, family_a.id)) == 1
    assert len(await activity_log_service.list_activity(db, family_b.id)) == 1


@pytest.mark.asyncio
async def test_activity_log_http_requires_family_members_read(db, client):
    family, manager, child = await _markpoint_family_with_two_members(db)
    await markpoint_service.create_mission(db, family.id, manager, assignee_id=child.id, title="숙제", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=10)
    await _grant_family_owner_role(db, manager.id)
    from app.domains.family import auth_service
    await auth_service.create_credential(db, manager.account_id, "log.manager", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "log.manager", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.get(f"/api/families/{family.id}/activity-log", headers=headers)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 1
    assert resp.json()[0]["actor_display_name"] == "Parent"

    other_family = FamilyGroup(name="unrelated", status="active")
    db.add(other_family)
    await db.commit()
    denied = await client.get(f"/api/families/{other_family.id}/activity-log", headers=headers)
    assert denied.status_code == 403


# --- SLICE-SEARCH (3j) -------------------------------------------------------


@pytest.mark.asyncio
async def test_search_finds_matching_mission_titles(db):
    family, manager, child = await _markpoint_family_with_two_members(db)
    await markpoint_service.create_mission(db, family.id, manager, assignee_id=child.id, title="여름 여행 짐 싸기", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=30)
    await markpoint_service.create_mission(db, family.id, manager, assignee_id=child.id, title="방 청소하기", scheduled_for=datetime.now(timezone.utc).date(), reward_amount=10)

    results = await search_service.search(db, family.id, child, "여행")
    assert [r["title"] for r in results if r["source"] == "mission"] == ["여름 여행 짐 싸기"]


@pytest.mark.asyncio
async def test_search_without_markpoint_access_returns_no_mission_results(db):
    family, parent, child = await _family_with_two_members(db)  # no ServiceSubscription -- no Markpoint access
    results = await search_service.search(db, family.id, parent, "아무거나")
    assert not any(r["source"] == "mission" for r in results)


@pytest.mark.asyncio
async def test_search_finds_wagle_messages_only_within_participants_visible_range(db, family_env):
    from tests.conftest import create_bare_membership
    admin, member, family_id = family_env["admin"], family_env["member"], family_env["family_id"]
    client = family_env["client"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "s1", "body": "이번 여름 여행 기대돼요"},
        headers=admin.headers,
    )
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "s2", "body": "오늘 저녁 뭐 먹지"},
        headers=member.headers,
    )

    admin_membership = await db.get(FamilyMembership, admin.membership_id)
    results = await search_service.search(db, family_id, admin_membership, "여행")
    assert [r["title"] for r in results if r["source"] == "message"] == ["이번 여름 여행 기대돼요"]

    outsider_id = await create_bare_membership(db, family_id, "outsider")
    outsider_membership = await db.get(FamilyMembership, outsider_id)
    outsider_results = await search_service.search(db, family_id, outsider_membership, "여행")
    assert not any(r["source"] == "message" for r in outsider_results)


@pytest.mark.asyncio
async def test_search_http_cross_family_denied(db, client):
    family, manager, child = await _markpoint_family_with_two_members(db)
    other_family = FamilyGroup(name="other-search-family", status="active")
    db.add(other_family)
    await db.commit()

    from app.domains.family import auth_service
    await auth_service.create_credential(db, manager.account_id, "search.manager", "Str0ngPassw0rd!")
    await db.commit()
    login = await client.post("/api/auth/account/login", json={"username": "search.manager", "password": "Str0ngPassw0rd!", "device_id": "d1"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    ok = await client.get(f"/api/families/{family.id}/search", params={"q": "미션"}, headers=headers)
    assert ok.status_code == 200

    denied = await client.get(f"/api/families/{other_family.id}/search", params={"q": "미션"}, headers=headers)
    assert denied.status_code == 403
