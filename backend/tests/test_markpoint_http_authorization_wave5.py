"""Wave 5 — the Markpoint HTTP authorization matrix, over real requests.

**Why these are HTTP and not service calls.** A service-level test proves the
service checks something; it cannot prove the *route* is wired to that check.
Every finding this file is meant to catch — a route that forgot its dependency,
a personal `/me` route reachable without a family, a 404-vs-403 that leaks
existence — lives in the wiring, not in the service. So every case below issues
a request through the app.

The distinction the matrix is most careful about:

- **403** — you are a member of this Family but lack this authority.
- **404** — the resource is not yours to know about. Used for cross-family
  access deliberately: a 403 there would confirm that an id exists in another
  Family, which is itself a disclosure.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select, text, update

from app.domains.family import auth_service
from app.domains.family.models import (
    Account,
    FamilyGroup,
    FamilyMembership,
    MembershipRoleAssignment,
    ServiceSubscription,
)
from app.domains.markpoint_access.models import MarkpointAccessRestriction
from app.domains.markpoint_target import service

PASSWORD = "Str0ngPassw0rd!"


async def _family(db, name, *, subscription="active"):
    f = FamilyGroup(name=name, status="active")
    db.add(f)
    await db.flush()
    if subscription is not None:
        db.add(
            ServiceSubscription(
                family_group_id=f.id,
                service_code="markpoint",
                status=subscription,
                started_at=datetime.now(timezone.utc),
            )
        )
    await db.flush()
    return f


async def _actor(db, client, family_id, name, *, roles=(), membership_status="active",
                 account_status="active"):
    """One fully-wired actor: Account + credential + login + membership + roles."""
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family_id,
        account_id=account.id,
        relationship="unknown",
        status=membership_status,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.flush()
    for code in roles:
        role_id = (
            await db.execute(
                text(
                    "SELECT id FROM roles WHERE scope_type='SERVICE' "
                    "AND service_code='markpoint' AND code=:code"
                ),
                {"code": code},
            )
        ).scalar_one()
        db.add(MembershipRoleAssignment(membership_id=membership.id, role_id=role_id))
    await auth_service.create_credential(db, account.id, f"{name}.{family_id}", PASSWORD)
    await db.commit()

    resp = await client.post(
        "/api/auth/account/login",
        json={"username": f"{name}.{family_id}", "password": PASSWORD, "device_id": f"d-{name}"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]

    if account_status != "active":
        await db.execute(update(Account).where(Account.id == account.id).values(status=account_status))
        await db.commit()

    return {"account": account, "membership": membership, "token": token,
            "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
async def env(db, client):
    """Two Families, and in the first one every actor shape the matrix needs."""
    family = await _family(db, "primary")
    other = await _family(db, "secondary")

    plain = await _actor(db, client, family.id, "plain")
    missions = await _actor(db, client, family.id, "missionmgr", roles=("mission_manager",))
    points = await _actor(db, client, family.id, "pointadmin", roles=("point_admin",))
    outsider = await _actor(db, client, other.id, "outsider", roles=("mission_manager",))

    mission = await service.create_mission(
        db, family.id, missions["membership"],
        assignee_id=plain["membership"].id, title="chore",
        scheduled_for=date.today(), reward_amount=10,
    )
    await db.commit()
    return {
        "family": family, "other": other, "plain": plain, "missions": missions,
        "points": points, "outsider": outsider, "mission": mission, "db": db, "client": client,
    }


def _paths(family_id: int, mission_id: int) -> dict[str, tuple[str, str, dict | None]]:
    """Every Markpoint resource the matrix covers, as (method, path, body)."""
    base = f"/api/families/{family_id}/markpoint"
    return {
        "config_read": ("get", f"{base}/config", None),
        "config_write": ("put", f"{base}/config", {"cycle_type": "weekly"}),
        "template_list": ("get", f"{base}/templates", None),
        "materialize_window": ("post", f"{base}/templates/materialize-window", None),
        "admin_missions": ("get", f"{base}/missions", None),
        "bulk_approve": ("post", f"{base}/missions/bulk-approve", {"mission_ids": [mission_id]}),
        "mission_approve": ("post", f"{base}/missions/{mission_id}/approve", None),
        "ledger_adjust": ("post", f"{base}/ledger/adjustments",
                          {"beneficiary_membership_id": 1, "amount": 5,
                           "reason": "x", "idempotency_key": "k"}),
    }


async def _call(client, method, path, body, headers=None, params=None):
    kwargs = {"headers": headers or {}}
    if params:
        kwargs["params"] = params
    if body is not None:
        return await getattr(client, method)(path, json=body, **kwargs)
    return await getattr(client, method)(path, **kwargs)


# ===========================================================================
# Session / account level
# ===========================================================================


async def test_every_markpoint_route_rejects_an_unauthenticated_caller(env):
    for name, (method, path, body) in _paths(env["family"].id, env["mission"].id).items():
        resp = await _call(env["client"], method, path, body)
        assert resp.status_code in (401, 403), f"{name}: {resp.status_code}"


async def test_personal_routes_reject_an_unauthenticated_caller(env):
    for path in (
        "/api/me/markpoint/missions", "/api/me/markpoint/balance", "/api/me/markpoint/level",
        "/api/me/markpoint/summary", "/api/me/markpoint/weekly", "/api/me/markpoint/projection",
        "/api/me/markpoint/deductions/history",
    ):
        resp = await env["client"].get(path, params={"family_id": env["family"].id})
        assert resp.status_code in (401, 403), f"{path}: {resp.status_code}"


async def test_a_suspended_account_is_refused_everywhere(env, db, client):
    suspended = await _actor(db, client, env["family"].id, "suspended",
                             roles=("mission_manager",), account_status="suspended")
    for name, (method, path, body) in _paths(env["family"].id, env["mission"].id).items():
        resp = await _call(client, method, path, body, headers=suspended["headers"])
        assert resp.status_code == 403, f"{name}: {resp.status_code}"


async def test_a_revoked_session_stops_working_immediately(env, db, client):
    from app.domains.family.models import AccountSession

    actor = env["missions"]
    session_row = (
        await db.execute(
            select(AccountSession).where(AccountSession.account_id == actor["account"].id)
        )
    ).scalars().first()
    await auth_service.logout(db, session_row.id)

    resp = await client.get(
        f"/api/families/{env['family'].id}/markpoint/config", headers=actor["headers"]
    )
    # Not "when the access token expires" — the Session is checked per request.
    assert resp.status_code == 401


# ===========================================================================
# Membership level
# ===========================================================================


async def test_a_suspended_membership_loses_access(env, db, client):
    suspended = await _actor(db, client, env["family"].id, "gone",
                             roles=("mission_manager",), membership_status="suspended")
    resp = await _call(client, "get", f"/api/families/{env['family'].id}/markpoint/config",
                       None, headers=suspended["headers"])
    assert resp.status_code == 403


async def test_cross_family_access_is_refused_for_every_resource(env, client):
    """An admin of another Family holds the same role code — the only thing
    stopping them is the Family scope, which is what this asserts."""
    for name, (method, path, body) in _paths(env["family"].id, env["mission"].id).items():
        resp = await _call(client, method, path, body, headers=env["outsider"]["headers"])
        assert resp.status_code in (403, 404), f"{name}: {resp.status_code}"


async def test_a_foreign_mission_id_is_not_found_rather_than_forbidden(env, db, client):
    """404, not 403: a 403 would confirm the id exists in another Family."""
    foreign_manager = await _actor(db, client, env["other"].id, "otherboss",
                                   roles=("mission_manager",))
    foreign_child = await _actor(db, client, env["other"].id, "otherkid")
    foreign_mission = await service.create_mission(
        db, env["other"].id, foreign_manager["membership"],
        assignee_id=foreign_child["membership"].id, title="theirs",
        scheduled_for=date.today(), reward_amount=3,
    )
    await db.commit()

    resp = await client.post(
        f"/api/families/{env['family'].id}/markpoint/missions/{foreign_mission.id}/approve",
        headers=env["missions"]["headers"],
    )
    assert resp.status_code == 404

    resp = await client.post(
        f"/api/families/{env['family'].id}/markpoint/missions/bulk-approve",
        json={"mission_ids": [foreign_mission.id]},
        headers=env["missions"]["headers"],
    )
    assert resp.status_code == 404


# ===========================================================================
# Markpoint access level
# ===========================================================================


async def test_an_inactive_subscription_blocks_the_whole_service(db, client):
    family = await _family(db, "unsubscribed", subscription="cancelled")
    actor = await _actor(db, client, family.id, "boss", roles=("mission_manager",))
    resp = await client.get(f"/api/families/{family.id}/markpoint/config",
                            headers=actor["headers"])
    assert resp.status_code == 403


async def test_an_active_restriction_blocks_the_restricted_member_only(env, db, client):
    restricted = await _actor(db, client, env["family"].id, "restricted")
    db.add(
        MarkpointAccessRestriction(
            family_group_id=env["family"].id,
            # The column is `target_membership_id` and the status enum is
            # upper-case ACTIVE — read from the Wave 4 model rather than
            # guessed from the neighbouring tables' naming.
            target_membership_id=restricted["membership"].id,
            status="ACTIVE",
            reason="test",
            restricted_by_membership_id=env["missions"]["membership"].id,
        )
    )
    await db.commit()

    blocked = await client.get("/api/me/markpoint/balance",
                               params={"family_id": env["family"].id},
                               headers=restricted["headers"])
    assert blocked.status_code == 403

    # The unrestricted member in the same Family is unaffected.
    allowed = await client.get("/api/me/markpoint/balance",
                               params={"family_id": env["family"].id},
                               headers=env["plain"]["headers"])
    assert allowed.status_code == 200


# ===========================================================================
# Permission level — D4: holding the Family is not holding the service
# ===========================================================================


async def test_a_plain_member_cannot_reach_any_admin_capability(env, client):
    admin_only = ("config_write", "materialize_window", "admin_missions",
                  "bulk_approve", "mission_approve", "ledger_adjust")
    paths = _paths(env["family"].id, env["mission"].id)
    for name in admin_only:
        method, path, body = paths[name]
        resp = await _call(client, method, path, body, headers=env["plain"]["headers"])
        assert resp.status_code == 403, f"{name}: {resp.status_code}"


async def test_a_family_owner_is_not_automatically_a_service_admin(env, db, client):
    """D4, and the reason migration `0006` stripped the Markpoint permissions
    from every FAMILY-scope role. Being the owner must not reach these."""
    owner = await _actor(db, client, env["family"].id, "owner")
    role_id = (
        await db.execute(
            text("SELECT id FROM roles WHERE scope_type='FAMILY' AND code='owner'")
        )
    ).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=owner["membership"].id, role_id=role_id))
    await db.commit()

    for name in ("config_write", "materialize_window", "bulk_approve", "ledger_adjust"):
        method, path, body = _paths(env["family"].id, env["mission"].id)[name]
        resp = await _call(client, method, path, body, headers=owner["headers"])
        assert resp.status_code == 403, f"family owner reached {name}: {resp.status_code}"


async def test_mission_and_point_permissions_are_separate(env, client):
    """`markpoint.missions.manage` must not confer `markpoint.points.adjust`."""
    paths = _paths(env["family"].id, env["mission"].id)

    method, path, body = paths["ledger_adjust"]
    resp = await _call(client, method, path, body, headers=env["missions"]["headers"])
    assert resp.status_code == 403, "mission manager reached a point adjustment"

    method, path, body = paths["bulk_approve"]
    resp = await _call(client, method, path, body, headers=env["points"]["headers"])
    assert resp.status_code == 403, "point admin reached a bulk approval"


async def test_the_right_permission_is_accepted(env, client):
    """The negative cases above are only meaningful if the positive one works."""
    resp = await client.get(f"/api/families/{env['family'].id}/markpoint/config",
                            headers=env["missions"]["headers"])
    assert resp.status_code == 200

    resp = await client.get(f"/api/families/{env['family'].id}/markpoint/missions",
                            headers=env["missions"]["headers"])
    assert resp.status_code == 200

    resp = await client.put(f"/api/families/{env['family'].id}/markpoint/config",
                            json={"cycle_type": "weekly"},
                            headers=env["missions"]["headers"])
    assert resp.status_code == 200


# ===========================================================================
# Personal routes
# ===========================================================================


async def test_personal_routes_serve_only_the_callers_own_data(env, db, client):
    """`/me` is scoped by the Session's Account and the path's family, never by
    a client-supplied membership id."""
    for path in ("/api/me/markpoint/weekly", "/api/me/markpoint/projection",
                 "/api/me/markpoint/deductions/history"):
        resp = await client.get(path, params={"family_id": env["family"].id},
                                headers=env["plain"]["headers"])
        assert resp.status_code == 200, f"{path}: {resp.text}"
        body = resp.json()
        if isinstance(body, dict) and "family_membership_id" in body:
            assert body["family_membership_id"] == env["plain"]["membership"].id


async def test_a_personal_route_refuses_a_family_the_caller_does_not_belong_to(env, client):
    resp = await client.get("/api/me/markpoint/projection",
                            params={"family_id": env["other"].id},
                            headers=env["plain"]["headers"])
    assert resp.status_code in (403, 404)
