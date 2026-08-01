"""Wave 1 — Account-native credential, Session, scoped RBAC and route authorization.

Covers the six Wave 1 Backlog tasks' own DoD:
`MONGLE-W1-ACCOUNT-CREDENTIAL-001`, `MONGLE-W1-ACCOUNT-SESSION-CONTEXT-001`,
`MONGLE-W1-SCOPED-RBAC-001`, `MONGLE-W1-FAMILY-SCOPED-ROUTE-AUTHZ-001`,
`MONGLE-W1-FAMILYADMIN-ACCOUNT-ISSUANCE-001`.

Every fixture here is synthetic and created inside the isolated Phase 2 test
database; nothing reads or writes operating data. No legacy player/admin row is
required to authenticate, which is the point of most of these assertions.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text

from app.domains.family import auth_service, service as family_service
from app.domains.family.models import (
    Account,
    AccountCredential,
    AccountSession,
    FamilyGroup,
    FamilyMembership,
    MembershipRoleAssignment,
    Role,
)

from tests.conftest import create_family


GOOD_PASSWORD = "Str0ngPassw0rd!"
OTHER_PASSWORD = "An0therPassw0rd!"


# --- helpers --------------------------------------------------------------


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


# --- Credential -----------------------------------------------------------


async def test_login_succeeds_with_no_legacy_identity_at_all(db, client):
    """The core D8 RESET assertion: an Account logs in with no player_auth,
    no admin_auth and no legacy_identity_mappings row anywhere."""
    await _account_with_login(db, "solo", "solo.user")

    body = await _login(client, "solo.user")

    assert body["access_token"]
    assert body["refresh_token"]
    assert body["is_password_change_required"] is False
    # Prove no legacy bridge was involved for this account.
    legacy_rows = (await db.execute(text("SELECT count(*) FROM legacy_identity_mappings"))).scalar_one()
    assert legacy_rows == 0


async def test_login_rejects_wrong_password_and_counts_the_attempt(db, client):
    account = await _account_with_login(db, "wrong", "wrong.user")

    resp = await client.post(
        "/api/auth/account/login",
        json={"username": "wrong.user", "password": "not-the-password", "device_id": "d1"},
    )
    assert resp.status_code == 401

    credential = await auth_service.get_credential_for_account(db, account.id)
    await db.refresh(credential)
    assert credential.failed_attempt_count == 1


async def test_login_is_locked_after_max_attempts(db, client):
    from app.config import settings

    await _account_with_login(db, "locky", "locky.user")

    for _ in range(settings.ACCOUNT_MAX_LOGIN_ATTEMPTS):
        resp = await client.post(
            "/api/auth/account/login",
            json={"username": "locky.user", "password": "bad", "device_id": "d1"},
        )
        assert resp.status_code == 401

    # Correct password now, but the credential is locked.
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": "locky.user", "password": GOOD_PASSWORD, "device_id": "d1"},
    )
    assert resp.status_code == 423


async def test_unknown_username_and_wrong_password_are_indistinguishable(db, client):
    await _account_with_login(db, "enum", "enum.user")

    unknown = await client.post(
        "/api/auth/account/login",
        json={"username": "does.not.exist", "password": GOOD_PASSWORD, "device_id": "d1"},
    )
    wrong = await client.post(
        "/api/auth/account/login",
        json={"username": "enum.user", "password": "bad-password", "device_id": "d1"},
    )
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json()["detail"] == wrong.json()["detail"]


async def test_password_is_never_stored_in_recoverable_form(db):
    account = await _account_with_login(db, "hashonly", "hash.user")

    credential = await auth_service.get_credential_for_account(db, account.id)
    assert credential.password_hash != GOOD_PASSWORD
    assert GOOD_PASSWORD not in credential.password_hash
    assert credential.password_hash.startswith("$2")  # bcrypt
    # No column anywhere on the row holds the plaintext.
    row = (
        await db.execute(text("SELECT * FROM account_credentials WHERE id = :i"), {"i": credential.id})
    ).mappings().one()
    assert not any(isinstance(v, str) and GOOD_PASSWORD in v for v in row.values())


async def test_duplicate_username_is_rejected_case_insensitively(db):
    from fastapi import HTTPException

    account_a = await _account_with_login(db, "first", "dup.user")
    account_b = await _make_account(db, "second")

    with pytest.raises(HTTPException) as exc:
        await auth_service.create_credential(db, account_b.id, "DUP.USER", GOOD_PASSWORD)
    assert exc.value.status_code == 409
    assert account_a.id != account_b.id


async def test_disabled_credential_cannot_log_in(db, client):
    account = await _account_with_login(db, "disabled", "disabled.user")
    credential = await auth_service.get_credential_for_account(db, account.id)
    credential.status = "disabled"
    await db.commit()

    resp = await client.post(
        "/api/auth/account/login",
        json={"username": "disabled.user", "password": GOOD_PASSWORD, "device_id": "d1"},
    )
    assert resp.status_code == 403


async def test_password_change_revokes_every_existing_session(db, client):
    await _account_with_login(db, "changer", "changer.user")
    first = await _login(client, "changer.user", device_id="d1")
    second = await _login(client, "changer.user", device_id="d2")

    resp = await client.post(
        "/api/me/password",
        json={"current_password": GOOD_PASSWORD, "new_password": OTHER_PASSWORD},
        headers=_bearer(first["access_token"]),
    )
    assert resp.status_code == 204

    # Both sessions, including the one that made the change, are now dead.
    for token in (first["access_token"], second["access_token"]):
        assert (await client.get("/api/me", headers=_bearer(token))).status_code == 401
    # And the new password works.
    await _login(client, "changer.user", password=OTHER_PASSWORD, device_id="d3")


# --- Session --------------------------------------------------------------


async def test_refresh_rotates_and_old_refresh_token_replay_is_rejected(db, client):
    await _account_with_login(db, "rotate", "rotate.user")
    first = await _login(client, "rotate.user")

    rotated = await client.post("/api/auth/account/refresh", json={"refresh_token": first["refresh_token"]})
    assert rotated.status_code == 200
    new_refresh = rotated.json()["refresh_token"]
    assert new_refresh != first["refresh_token"]

    replay = await client.post("/api/auth/account/refresh", json={"refresh_token": first["refresh_token"]})
    assert replay.status_code == 401


async def test_refresh_token_is_stored_only_as_a_hash(db, client):
    await _account_with_login(db, "hashref", "hashref.user")
    body = await _login(client, "hashref.user")

    stored = (await db.execute(select(AccountSession.refresh_token_hash))).scalars().all()
    assert stored
    assert body["refresh_token"] not in stored
    assert auth_service.hash_refresh_token(body["refresh_token"]) in stored


async def test_revoked_session_is_rejected_even_with_an_unexpired_access_token(db, client):
    await _account_with_login(db, "revoked", "revoked.user")
    body = await _login(client, "revoked.user")
    assert (await client.get("/api/me", headers=_bearer(body["access_token"]))).status_code == 200

    logout = await client.post("/api/auth/account/logout", headers=_bearer(body["access_token"]))
    assert logout.status_code == 204

    # The JWT itself is still within its TTL; the Session is what stops it.
    assert (await client.get("/api/me", headers=_bearer(body["access_token"]))).status_code == 401


async def test_logout_does_not_sign_out_other_devices(db, client):
    await _account_with_login(db, "multi", "multi.user")
    phone = await _login(client, "multi.user", device_id="phone")
    tablet = await _login(client, "multi.user", device_id="tablet")

    await client.post("/api/auth/account/logout", headers=_bearer(phone["access_token"]))

    assert (await client.get("/api/me", headers=_bearer(phone["access_token"]))).status_code == 401
    assert (await client.get("/api/me", headers=_bearer(tablet["access_token"]))).status_code == 200


async def test_device_unlink_revokes_only_that_device(db, client):
    await _account_with_login(db, "unlink", "unlink.user")
    phone_a = await _login(client, "unlink.user", device_id="phone")
    phone_b = await _login(client, "unlink.user", device_id="phone")
    tablet = await _login(client, "unlink.user", device_id="tablet")

    resp = await client.delete("/api/me/devices/phone", headers=_bearer(tablet["access_token"]))
    assert resp.status_code == 204

    # Both sessions on that device are gone; the other device is untouched.
    for token in (phone_a["access_token"], phone_b["access_token"]):
        assert (await client.get("/api/me", headers=_bearer(token))).status_code == 401
    assert (await client.get("/api/me", headers=_bearer(tablet["access_token"]))).status_code == 200


async def test_expired_session_is_rejected(db, client):
    await _account_with_login(db, "expired", "expired.user")
    body = await _login(client, "expired.user")

    session_row = (await db.execute(select(AccountSession))).scalars().first()
    session_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db.commit()

    assert (await client.get("/api/me", headers=_bearer(body["access_token"]))).status_code == 401


async def test_legacy_player_token_cannot_authenticate_an_account_route(db, client):
    """A legacy PIN-issued token must not satisfy the Account-native dependency."""
    from tests.conftest import auth_headers

    await _account_with_login(db, "legacyish", "legacyish.user")

    resp = await client.get("/api/me", headers=auth_headers(player_id=1))
    assert resp.status_code == 401


async def test_missing_and_malformed_tokens_are_rejected(client):
    assert (await client.get("/api/me")).status_code == 401
    assert (await client.get("/api/me", headers=_bearer("not-a-jwt"))).status_code == 401


# --- AuthorizedFamilySet / Family Context ---------------------------------


async def test_authorized_family_set_lists_every_active_membership(db, client):
    account = await _account_with_login(db, "multifam", "multifam.user")
    family_a = await create_family(db, "A")
    family_b = await create_family(db, "B")
    await _make_membership(db, family_a, account.id)
    await _make_membership(db, family_b, account.id)
    await db.commit()

    body = await _login(client, "multifam.user")
    me = await client.get("/api/me", headers=_bearer(body["access_token"]))
    assert me.status_code == 200

    ids = {f["family_group_id"] for f in me.json()["authorized_families"]}
    assert ids == {family_a, family_b}


async def test_ending_one_membership_keeps_the_account_session_and_other_family(db, client):
    """D3: one family leaving must not log the Account out or affect family B."""
    account = await _account_with_login(db, "leaver", "leaver.user")
    family_a = await create_family(db, "A")
    family_b = await create_family(db, "B")
    membership_a = await _make_membership(db, family_a, account.id)
    await _make_membership(db, family_b, account.id)
    await db.commit()

    body = await _login(client, "leaver.user")
    membership_a.status = "left"
    await db.commit()

    me = await client.get("/api/me", headers=_bearer(body["access_token"]))
    # Session still valid ...
    assert me.status_code == 200
    # ... but family A is no longer authorized, and B still is.
    ids = {f["family_group_id"] for f in me.json()["authorized_families"]}
    assert ids == {family_b}


async def test_inactive_family_is_excluded_from_the_authorized_set(db, client):
    account = await _account_with_login(db, "closedfam", "closedfam.user")
    family_id = await create_family(db, "Closing")
    await _make_membership(db, family_id, account.id)
    family = await db.get(FamilyGroup, family_id)
    family.status = "closed"
    await db.commit()

    body = await _login(client, "closedfam.user")
    me = await client.get("/api/me", headers=_bearer(body["access_token"]))
    assert me.json()["authorized_families"] == []


# --- Scoped RBAC ----------------------------------------------------------


async def test_membership_termination_revokes_its_role_assignments(db):
    account = await _make_account(db, "roleholder")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    assert len(await family_service.family_roles(db, membership.id)) == 1

    await family_service.update_membership(db, membership, None, "left")

    assert await family_service.family_roles(db, membership.id) == []
    assignment = (
        await db.execute(select(MembershipRoleAssignment).where(MembershipRoleAssignment.membership_id == membership.id))
    ).scalars().one()
    assert assignment.revoked_at is not None


async def test_family_admin_gets_no_automatic_service_admin_authority(db):
    """D4: a FamilyAdmin holds no Markpoint ServiceAdmin permission implicitly."""
    account = await _make_account(db, "familyadmin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    granted = await family_service.effective_permissions(db, membership)
    service_roles = [r for r in await family_service.family_roles(db, membership.id) if r.scope_type == "SERVICE"]

    assert "family.members.provision" in granted
    assert service_roles == []
    assert "markpoint.points.adjust" not in granted


async def test_plain_member_is_denied_by_default(db):
    account = await _make_account(db, "plain")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await _grant_family_role(db, membership.id, "member")
    await db.commit()

    granted = await family_service.effective_permissions(db, membership)
    assert "family.members.provision" not in granted
    assert "family.roles.assign" not in granted


async def test_last_owner_cannot_be_deactivated(db):
    from fastapi import HTTPException

    account = await _make_account(db, "onlyowner")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, account.id)
    await _grant_family_role(db, membership.id, "owner")
    await db.commit()

    with pytest.raises(HTTPException) as exc:
        await family_service.update_membership(db, membership, None, "removed")
    assert exc.value.status_code == 409


async def test_role_assignment_records_its_issuer_for_audit(db):
    actor = await _make_account(db, "assigner")
    target = await _make_account(db, "assignee")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, target.id)
    await db.commit()

    assignment = await family_service.assign_role(db, family_id, membership, "member", None, actor.id)

    assert assignment.assigned_by_account_id == actor.id
    assert assignment.assigned_at is not None


# --- Family-scoped route authorization ------------------------------------


async def test_family_route_denies_a_non_member(db, client):
    outsider = await _account_with_login(db, "outsider", "outsider.user")
    family_id = await create_family(db, "Private")
    await db.commit()

    body = await _login(client, "outsider.user")
    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "x", "username": "x.user"},
        headers=_bearer(body["access_token"]),
    )
    assert resp.status_code == 403
    assert outsider.id


async def test_family_route_denies_cross_family_access(db, client):
    """An admin of family A gets no authority over family B by substituting the id."""
    admin = await _account_with_login(db, "adminA", "admin.a")
    family_a = await create_family(db, "A")
    family_b = await create_family(db, "B")
    membership_a = await _make_membership(db, family_a, admin.id)
    await _grant_family_role(db, membership_a.id, "admin")
    await db.commit()

    body = await _login(client, "admin.a")
    resp = await client.post(
        f"/api/families/{family_b}/member-accounts",
        json={"display_name": "intruder", "username": "intruder.user"},
        headers=_bearer(body["access_token"]),
    )
    assert resp.status_code == 403


async def test_family_route_denies_a_suspended_membership(db, client):
    admin = await _account_with_login(db, "suspended", "suspended.admin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, admin.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    body = await _login(client, "suspended.admin")
    membership.status = "suspended"
    await db.commit()

    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "x", "username": "x.user"},
        headers=_bearer(body["access_token"]),
    )
    assert resp.status_code == 403


async def test_family_route_requires_authentication(db, client):
    family_id = await create_family(db)
    await db.commit()

    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "x", "username": "x.user"},
    )
    assert resp.status_code == 401


# --- FamilyAdmin Account issuance -----------------------------------------


async def test_family_admin_provisions_a_working_independent_account(db, client):
    admin = await _account_with_login(db, "issuer", "issuer.admin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, admin.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    body = await _login(client, "issuer.admin")
    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "child", "username": "Child.User", "relationship": "child"},
        headers=_bearer(body["access_token"]),
    )
    assert resp.status_code == 201, resp.text
    issued = resp.json()
    assert issued["is_password_change_required"] is True
    assert issued["username"] == "child.user"

    # The issued account is a real, independent, immediately usable login.
    new_login = await _login(client, "child.user", password=issued["initial_password"], device_id="child-device")
    assert new_login["account_id"] == issued["account_id"]
    assert new_login["account_id"] != admin.id
    assert new_login["is_password_change_required"] is True

    # And it lands in the right family.
    me = await client.get("/api/me", headers=_bearer(new_login["access_token"]))
    assert [f["family_group_id"] for f in me.json()["authorized_families"]] == [family_id]


async def test_issued_initial_password_is_only_a_hash_afterwards(db, client):
    admin = await _account_with_login(db, "issuer2", "issuer2.admin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, admin.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    body = await _login(client, "issuer2.admin")
    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "kid", "username": "kid.user"},
        headers=_bearer(body["access_token"]),
    )
    initial_password = resp.json()["initial_password"]

    credential = (
        await db.execute(select(AccountCredential).where(AccountCredential.username == "kid.user"))
    ).scalars().one()
    assert credential.password_hash != initial_password
    assert credential.issued_by_account_id == admin.id
    assert credential.is_initial_credential is True
    # There is no route that returns the password again.
    assert credential.is_password_change_required is True


async def test_plain_member_cannot_provision_accounts(db, client):
    member = await _account_with_login(db, "plainmember", "plain.member")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, member.id)
    await _grant_family_role(db, membership.id, "member")
    await db.commit()

    body = await _login(client, "plain.member")
    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "x", "username": "x.user"},
        headers=_bearer(body["access_token"]),
    )
    assert resp.status_code == 403


async def test_duplicate_username_issuance_rolls_back_the_whole_unit(db, client):
    """A rejected issuance must not leave a stranded Account or Membership."""
    admin = await _account_with_login(db, "issuer3", "issuer3.admin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, admin.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    accounts_before = (await db.execute(text("SELECT count(*) FROM accounts"))).scalar_one()
    memberships_before = (await db.execute(text("SELECT count(*) FROM family_memberships"))).scalar_one()

    body = await _login(client, "issuer3.admin")
    resp = await client.post(
        f"/api/families/{family_id}/member-accounts",
        json={"display_name": "dupe", "username": "issuer3.admin"},
        headers=_bearer(body["access_token"]),
    )
    assert resp.status_code == 409

    assert (await db.execute(text("SELECT count(*) FROM accounts"))).scalar_one() == accounts_before
    assert (await db.execute(text("SELECT count(*) FROM family_memberships"))).scalar_one() == memberships_before


async def test_family_admin_cannot_read_a_members_password_or_impersonate(db, client):
    """D2/D4: issuance grants no ongoing read access to the credential."""
    admin = await _account_with_login(db, "issuer4", "issuer4.admin")
    family_id = await create_family(db)
    membership = await _make_membership(db, family_id, admin.id)
    await _grant_family_role(db, membership.id, "admin")
    await db.commit()

    body = await _login(client, "issuer4.admin")
    issued = (
        await client.post(
            f"/api/families/{family_id}/member-accounts",
            json={"display_name": "target", "username": "target.user"},
            headers=_bearer(body["access_token"]),
        )
    ).json()

    # The admin's own /api/me is still the admin's; issuance produced no token
    # for the target and no route exposes the target's credential.
    me = await client.get("/api/me", headers=_bearer(body["access_token"]))
    assert me.json()["account_id"] == admin.id
    assert me.json()["account_id"] != issued["account_id"]

    # Neither the target's one-time password nor its stored hash leaks into any
    # response the admin can obtain. (Asserted against the real secret values
    # rather than the substring "password", which legitimately appears in the
    # `is_password_change_required` field name.)
    target_credential = (
        await db.execute(select(AccountCredential).where(AccountCredential.username == "target.user"))
    ).scalars().one()
    serialized = str(me.json())
    assert issued["initial_password"] not in serialized
    assert target_credential.password_hash not in serialized

    sessions = await client.get("/api/me/sessions", headers=_bearer(body["access_token"]))
    sessions_body = str(sessions.json())
    assert issued["initial_password"] not in sessions_body
    assert target_credential.password_hash not in sessions_body
