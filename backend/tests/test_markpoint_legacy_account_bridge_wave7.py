"""MONGLE-W7-4-LEGACY-MARKPOINT-ACCOUNT-BRIDGE-REMEDIATION-001.

Every `/api/me/markpoint/*` route used `Depends(get_current_account)`
(`family.dependencies`), the strict Account-native-only resolver Wagle's
realtime gateway deliberately relies on rejecting legacy-PIN tokens for (D3).
That made these core, non-optional routes 401 for any valid legacy-PIN
session, and the frontend's global interceptor read that 401 as "session
expired" and force-logged the user out — reproducing, on the Markpoint
screen, the exact class of defect
`MONGLE-W7-4-MARKPOINT-ADMIN-ROUTE-AND-LEGACY-NOTIFICATION-SESSION-
REMEDIATION-001` had just fixed for `/api/me/notifications` one screen
earlier. `_me` (the private dependency all nine `/api/me/markpoint/*` routes
share) now resolves through `get_current_user` + `family.service.
resolve_current_account` instead — the same legacy-bridge-aware pair
`/api/account-context` and the `/admin` legacy-JWT bridge already use.
`get_family_membership` (shared by many other domains' routers) and
`get_current_account` itself are untouched, so this file also asserts they
were not accidentally widened.

Over real HTTP requests, matching this suite's own
`test_markpoint_http_authorization_wave5.py` philosophy: a service-level
check cannot prove the route is wired to it.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import bcrypt
import pytest
from sqlalchemy import text, update

from app.domains.auth.models import PlayerAuth
from app.domains.family import auth_service, service
from app.domains.family.models import (
    Account,
    FamilyGroup,
    FamilyMembership,
    LegacyIdentityMapping,
    MembershipRoleAssignment,
    ServiceSubscription,
)
from app.domains.markpoint_target import service as mp_service
from app.domains.player.models import Player

PASSWORD = "Str0ngPassw0rd!"
PIN = "1234"
PIN_HASH = bcrypt.hashpw(PIN.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# All nine `/api/me/markpoint/*` reads sharing the fixed `_me` dependency —
# the four the frontend's own `MarkpointUser.tsx` `Promise.all` calls
# (`projection`/`weekly`/`level`/`deductions/history`, the ones the prior
# Independent Re-QA's browser reproduction actually observed 401ing) plus the
# five siblings the route inventory in this file's own module turned up.
ME_MARKPOINT_GET_PATHS = (
    "missions", "ledger", "balance", "level", "summary",
    "deductions", "weekly", "projection", "deductions/history",
)


async def _family(db, name, *, subscription="active"):
    f = FamilyGroup(name=name, status="active")
    db.add(f)
    await db.flush()
    if subscription is not None:
        db.add(
            ServiceSubscription(
                family_group_id=f.id, service_code="markpoint",
                status=subscription, started_at=datetime.now(timezone.utc),
            )
        )
    await db.flush()
    return f


async def _account_actor(db, client, family_id, name, *, roles=()):
    """An Account-native actor — same shape as the Wave 5 matrix's own `_actor`."""
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family_id, account_id=account.id,
        relationship="unknown", status="active", joined_at=datetime.now(timezone.utc),
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
    return {"account": account, "membership": membership,
            "headers": {"Authorization": f"Bearer {token}"}}


async def _legacy_player(db, name) -> Player:
    player = Player(name=name, role="player")
    db.add(player)
    await db.flush()
    db.add(PlayerAuth(player_id=player.id, pin_hash=PIN_HASH, is_admin=False))
    await db.flush()
    return player


async def _login_legacy(client, player_id: int) -> dict:
    resp = await client.post("/api/auth/login", json={"player_id": player_id, "pin": PIN})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}}


async def _mapped_legacy_actor(db, client, family_id, name, *, roles=(), mapping_status="linked"):
    """A legacy-PIN player bridged to a canonical Account with an active
    Family membership — the exact shape this remediation makes work."""
    account = Account(display_name=name, status="active")
    db.add(account)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family_id, account_id=account.id,
        relationship="unknown", status="active", joined_at=datetime.now(timezone.utc),
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
    player = await _legacy_player(db, name)
    db.add(LegacyIdentityMapping(
        account_id=account.id, legacy_system="markpoint",
        legacy_identity_type="player_auth", legacy_identity_id=str(player.id),
        mapping_status=mapping_status,
    ))
    await db.commit()
    legacy = await _login_legacy(client, player.id)
    return {"account": account, "membership": membership, "player": player,
            "headers": legacy["headers"]}


@pytest.fixture
async def env(db, client):
    family = await _family(db, "primary")
    other = await _family(db, "secondary")

    legacy_owner = await _mapped_legacy_actor(
        db, client, family.id, "legacyowner", roles=("mission_manager",),
    )
    native_peer = await _account_actor(db, client, family.id, "nativepeer")

    mission = await mp_service.create_mission(
        db, family.id, legacy_owner["membership"],
        assignee_id=legacy_owner["membership"].id, title="chore",
        scheduled_for=date.today(), reward_amount=10,
    )
    await db.commit()
    return {
        "db": db, "client": client, "family": family, "other": other,
        "legacy_owner": legacy_owner, "native_peer": native_peer, "mission": mission,
    }


async def _get(client, path, headers, family_id):
    return await client.get(f"/api/me/markpoint/{path}", headers=headers, params={"family_id": family_id})


# ---------------------------------------------------------------------------
# 12.1 — normal legacy: every /api/me/markpoint/* GET, 200
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ME_MARKPOINT_GET_PATHS)
async def test_legacy_bridged_session_reaches_every_me_markpoint_get(env, path):
    resp = await _get(env["client"], path, env["legacy_owner"]["headers"], env["family"].id)
    assert resp.status_code == 200, (path, resp.text)


async def test_legacy_bridged_session_matches_account_native_shape_for_the_same_person(db, client):
    """The bridge must resolve to the *same* canonical Account/Membership a
    native login for the same person would -- not a parallel, possibly
    divergent identity. Verified by comparing real, non-empty mission data
    returned through both credential paths for one underlying person."""
    family = await _family(db, "identity-parity")
    account = Account(display_name="dual", status="active")
    db.add(account)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family.id, account_id=account.id,
        relationship="unknown", status="active", joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.flush()
    role_id = (await db.execute(text(
        "SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='markpoint' AND code='mission_manager'"
    ))).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=membership.id, role_id=role_id))
    player = await _legacy_player(db, "dual")
    db.add(LegacyIdentityMapping(
        account_id=account.id, legacy_system="markpoint",
        legacy_identity_type="player_auth", legacy_identity_id=str(player.id),
        mapping_status="linked",
    ))
    await auth_service.create_credential(db, account.id, "dual.native", PASSWORD)
    await db.commit()

    mission = await mp_service.create_mission(
        db, family.id, membership, assignee_id=membership.id,
        title="parity-check", scheduled_for=date.today(), reward_amount=15,
    )
    await db.commit()

    legacy_headers = (await _login_legacy(client, player.id))["headers"]
    native_resp = await client.post(
        "/api/auth/account/login",
        json={"username": "dual.native", "password": PASSWORD, "device_id": "d-dual"},
    )
    assert native_resp.status_code == 200, native_resp.text
    native_headers = {"Authorization": f"Bearer {native_resp.json()['access_token']}"}

    legacy_body = (await _get(client, "missions", legacy_headers, family.id)).json()
    native_body = (await _get(client, "missions", native_headers, family.id)).json()
    assert legacy_body == native_body
    assert len(legacy_body) == 1
    assert legacy_body[0]["id"] == mission.id
    assert legacy_body[0]["title"] == "parity-check"


# ---------------------------------------------------------------------------
# 12.2 — Account-native regression
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ME_MARKPOINT_GET_PATHS)
async def test_account_native_session_still_reaches_every_me_markpoint_get(env, path):
    resp = await _get(env["client"], path, env["native_peer"]["headers"], env["family"].id)
    assert resp.status_code == 200, (path, resp.text)


# ---------------------------------------------------------------------------
# 12.3 — no canonical mapping: safe rejection, same bridge contract as
# /api/account-context (403, not a fabricated 200)
# ---------------------------------------------------------------------------


async def test_legacy_token_with_no_mapping_is_rejected_not_faked(db, client):
    family = await _family(db, "unmapped-family")
    player = await _legacy_player(db, "unmapped")
    await db.commit()
    headers = (await _login_legacy(client, player.id))["headers"]

    resp = await _get(client, "level", headers, family.id)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "계정 매핑이 필요합니다"


async def test_legacy_mapping_not_yet_linked_is_rejected(db, client):
    """`mapping_status` other than `linked` (e.g. `candidate`) must not be
    treated as authorization -- same rule `resolve_current_account` already
    enforces for every other consumer of the bridge."""
    family = await _family(db, "candidate-family")
    actor = await _mapped_legacy_actor(
        db, client, family.id, "candidatemap", mapping_status="candidate",
    )
    resp = await _get(client, "level", actor["headers"], family.id)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "계정 매핑이 필요합니다"


# ---------------------------------------------------------------------------
# 12.4 / 12.5 — no membership in the target Family / cross-family, zero leak
# ---------------------------------------------------------------------------


async def test_legacy_session_denied_for_a_family_it_has_no_membership_in(env):
    resp = await _get(env["client"], "level", env["legacy_owner"]["headers"], env["other"].id)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "활성 가족 구성원 권한이 필요합니다"


async def test_legacy_session_cannot_read_another_familys_missions(env):
    """Cross-family: the *other* Family's own missions endpoint, same 403,
    and — since the same-family case above already proves 200 with real
    data — this specific 403 proves zero leakage rather than an unrelated
    empty result."""
    resp = await _get(env["client"], "missions", env["legacy_owner"]["headers"], env["other"].id)
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 12.6 — mapped + member, but the Family's own Markpoint subscription is not
# active: existing access-layer contract (403), unaffected by this fix
# ---------------------------------------------------------------------------


async def test_legacy_session_with_membership_but_inactive_subscription_still_403s(db, client):
    family = await _family(db, "inactive-sub-family", subscription="cancelled")
    actor = await _mapped_legacy_actor(db, client, family.id, "nosub")
    resp = await _get(client, "level", actor["headers"], family.id)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Markpoint 접근 권한이 없습니다"


# ---------------------------------------------------------------------------
# 12.7 / 12.8 — unauthenticated / forged or malformed token
# ---------------------------------------------------------------------------


async def test_no_token_is_401(env):
    resp = await _get(env["client"], "level", {}, env["family"].id)
    assert resp.status_code == 401


async def test_forged_token_is_401(env):
    resp = await _get(env["client"], "level", {"Authorization": "Bearer not.a.real.token"}, env["family"].id)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Blast-radius guards: the fix is scoped to `_me` only. Neither the shared
# `get_family_membership` dependency (used by many other domains) nor
# `get_current_account` itself (which Wagle's realtime gateway deliberately
# relies on staying legacy-exclusive, D3) was widened.
# ---------------------------------------------------------------------------


async def test_family_scoped_admin_markpoint_route_still_rejects_a_legacy_token(env):
    """`get_family_membership` (the dependency every `/api/families/{id}/
    markpoint/*` admin/mutation route uses) was not touched -- a legacy-PIN
    token must still be refused there exactly as before this fix."""
    resp = await env["client"].get(
        f"/api/families/{env['family'].id}/markpoint/templates",
        headers=env["legacy_owner"]["headers"],
    )
    assert resp.status_code == 401


async def test_wagle_realtime_dependency_still_rejects_a_legacy_token(env):
    """`get_current_account` itself (Wagle's realtime gateway's own D3
    Account-native-only boundary) must be completely unaffected by this fix."""
    resp = await env["client"].get(
        "/api/me/wagle/realtime-context", headers=env["legacy_owner"]["headers"],
    )
    assert resp.status_code == 401
