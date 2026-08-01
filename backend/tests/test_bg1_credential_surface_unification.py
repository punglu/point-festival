"""BG-1 — Account-native tokens on the legacy-shaped `get_current_user` chain.

`MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001` found that no single credential
reached both the family-context API (behind `app.dependencies.get_current_user`,
originally `{player, admin}` only) and the Markpoint Target API (Account-native
only). The fix widens `get_current_user` to also accept an `account`-role
token and teaches `family.service.resolve_current_account` to resolve it.

That resolution is security-sensitive: it must apply the exact same
Session-liveness and Account-active checks that
`family.dependencies.get_current_account` already enforced for Account-native
routes, and it must never let an Account token's `sub` (an `account_id`) be
mistaken for a legacy `player_id` on a route that wasn't meant to accept it.
Both properties are now enforced by one shared function,
`auth_service.resolve_account_from_session_claim`, consumed by both
`get_current_account` and `resolve_current_account`. These tests pin that
behavior at the HTTP layer so a future edit to either call site can't
reintroduce the two-copies drift the refactor removed.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from jose import jwt
from sqlalchemy import select

from app.config import settings
from app.domains.family import auth_service
from app.domains.family.auth_service import ACCOUNT_TOKEN_ROLE
from app.domains.family.models import Account, AccountSession

from tests.conftest import auth_headers, create_family, _create_legacy_player


GOOD_PASSWORD = "Str0ngPassw0rd!"


async def _account_with_login(db, display_name: str, username: str) -> Account:
    account = Account(display_name=display_name, status="active")
    db.add(account)
    await db.flush()
    await auth_service.create_credential(db, account.id, username, GOOD_PASSWORD)
    await db.commit()
    return account


async def _login(client, username: str) -> dict:
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": username, "password": GOOD_PASSWORD, "device_id": "device-a"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_account_context_accepts_an_account_native_token(db, client):
    """The BG-1 fix itself: an Account Session now reaches the family-context route."""
    account = await _account_with_login(db, "bg1-happy", "bg1.happy")
    body = await _login(client, "bg1.happy")

    resp = await client.get("/api/account-context", headers=_bearer(body["access_token"]))

    assert resp.status_code == 200
    assert resp.json()["account_id"] == account.id


async def test_revoked_session_is_rejected_identically_by_both_entry_points(db, client):
    """The exact drift the refactor closed: `/api/me` (get_current_account) and
    `/api/account-context` (get_current_user -> resolve_current_account) must
    agree, because both now call the one shared session-liveness check."""
    await _account_with_login(db, "bg1-revoked", "bg1.revoked")
    body = await _login(client, "bg1.revoked")
    token = body["access_token"]

    assert (await client.get("/api/me", headers=_bearer(token))).status_code == 200
    assert (await client.get("/api/account-context", headers=_bearer(token))).status_code == 200

    await client.post("/api/auth/account/logout", headers=_bearer(token))

    # Same still-unexpired JWT, both routes, both must now reject it.
    assert (await client.get("/api/me", headers=_bearer(token))).status_code == 401
    assert (await client.get("/api/account-context", headers=_bearer(token))).status_code == 401


async def test_deactivated_account_is_rejected_via_the_legacy_shaped_entry_point(db, client):
    """`get_current_account` already enforced Account.status == "active"; confirm
    the `get_current_user` -> `resolve_current_account` path enforces it too."""
    account = await _account_with_login(db, "bg1-deactivated", "bg1.deactivated")
    body = await _login(client, "bg1.deactivated")

    account.status = "suspended"
    await db.commit()

    resp = await client.get("/api/account-context", headers=_bearer(body["access_token"]))
    assert resp.status_code == 403


async def test_widened_role_set_does_not_bypass_a_route_that_only_accepts_player_or_admin(db, client):
    """`get_current_user` now accepts an `account`-role token, but a route that
    explicitly gates on role in {player, admin} (feedback listing) must still
    reject it with 403, not silently misread its `sub` as a player_id."""
    await _account_with_login(db, "bg1-feedback", "bg1.feedback")
    body = await _login(client, "bg1.feedback")

    resp = await client.get(
        "/api/feedbacks/", params={"date": date.today().isoformat()}, headers=_bearer(body["access_token"])
    )
    assert resp.status_code == 403


async def test_account_id_colliding_with_a_legacy_player_id_is_not_confused(db, client):
    """Worst case for the identity-confusion risk this branch could have
    introduced: an Account and a legacy Player that happen to share the same
    numeric id. A role-gated legacy route must still reject the Account token
    outright rather than ever treating its `sub` as that player's id."""
    account = await _account_with_login(db, "bg1-collide", "bg1.collide")
    player_id = await _create_legacy_player(db, "collide-legacy")
    await db.commit()
    assert account.id == player_id  # both are the first row of a freshly truncated table

    account_body = await _login(client, "bg1.collide")
    account_resp = await client.get(
        "/api/feedbacks/",
        params={"date": date.today().isoformat()},
        headers=_bearer(account_body["access_token"]),
    )
    assert account_resp.status_code == 403

    legacy_resp = await client.get(
        "/api/feedbacks/",
        params={"date": date.today().isoformat()},
        headers=auth_headers(player_id),
    )
    assert legacy_resp.status_code == 200


def _validly_signed_token_with(**overrides) -> str:
    payload = {
        "sub": "1",
        "role": ACCOUNT_TOKEN_ROLE,
        "sid": 1,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    payload.update(overrides)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def test_non_numeric_sid_is_rejected_as_401_not_a_server_error(db, client):
    """`MONGLE-W6-BG1-CREDENTIAL-SURFACE-FIX-001-INDEPENDENT-QA-001` found that
    a validly-signed Account token with a non-numeric `sid` escaped the auth
    contract as an unhandled `ValueError` from `int(session_id)` (a 500)
    instead of the 401 every other malformed-claim case in
    `resolve_account_from_session_claim` produces. Exercised through both
    entry points that call it."""
    await _account_with_login(db, "bg1-badsid", "bg1.badsid")

    token = _validly_signed_token_with(sid="bad")

    assert (await client.get("/api/me", headers=_bearer(token))).status_code == 401
    assert (await client.get("/api/account-context", headers=_bearer(token))).status_code == 401
