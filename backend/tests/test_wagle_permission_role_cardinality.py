"""MONGLE-W7-4-WAGLE-MULTI-ROLE-CARDINALITY-REMEDIATION-001.

`_require_permission`'s READ "retained access" check
(`app/domains/wagle/service.py`) used `scalar_one_or_none()` on a query that
can legitimately return more than one row: a membership holding two or more
currently-active roles that each grant `wagle.messages.read` (e.g.
`participant` and `room_admin` both do, per migration 0002) raised
`MultipleResultsFound` -- uncaught, surfacing as an HTTP 500 on every Wagle
read endpoint for that membership. Fixed with `.limit(1)`, since the check
is existence-only ("does any active role grant READ"), not a lookup of a
specific row.
"""
from __future__ import annotations

from sqlalchemy import text

from app.domains.family.models import MembershipRoleAssignment
from tests.conftest import create_actor, create_family, set_subscription


async def _grant_role(db, membership_id: int, role_code: str) -> None:
    """Add one more active MembershipRoleAssignment for an already-existing
    membership, without touching the (untruncated, Alembic-owned) roles
    registry -- mirrors create_actor's own role lookup."""
    role_id = (
        await db.execute(
            text("SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='wagle' AND code=:code"),
            {"code": role_code},
        )
    ).scalar_one()
    db.add(MembershipRoleAssignment(membership_id=membership_id, role_id=role_id))
    await db.commit()


async def test_two_roles_granting_the_same_permission_no_500(family_env):
    """The exact reported shape: participant (READ+SEND) + room_admin
    (READ+SEND+manage) on one membership -- both grant READ."""
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    member = family_env["member"]  # already has 'participant'
    await _grant_role(db, member.membership_id, "room_admin")

    resp = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=member.headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_three_roles_granting_the_same_permission_no_500(family_env):
    """Three MembershipRoleAssignment rows for one membership, all resolving
    to a READ-granting role -- the cardinality-3 boundary, not just 2.

    `uq_active_membership_role` (migration 0001, a real pre-existing
    invariant, confirmed by triggering it directly) is a partial unique
    index on (membership_id, role_id) WHERE revoked_at IS NULL -- one
    membership cannot hold the *same* role twice while active. The codebase
    also only ever seeds 2 SERVICE/wagle roles (`participant`, `room_admin`)
    that grant `wagle.messages.read`. Reaching a genuine 3rd row therefore
    needs a 3rd *distinct* role; this test inserts one, scoped and named
    only for this test, and deletes it (role_permissions link, then the
    role) in a `finally` -- `roles`/`role_permissions` are Alembic-owned
    registry tables the suite's own reset_db fixture deliberately does not
    truncate between tests, so leaving it behind would leak into every
    later test in the same pytest session."""
    from sqlalchemy import text as sa_text

    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    member = family_env["member"]  # already has 'participant' (row 1)
    await _grant_role(db, member.membership_id, "room_admin")  # row 2

    role_id = (
        await db.execute(
            sa_text(
                "INSERT INTO roles (scope_type, service_code, code, name, description, is_active) "
                "VALUES ('SERVICE', 'wagle', 'qa_cardinality_extra_reader_001', "
                "'QA cardinality extra reader (test-only)', 'test-only, deleted at teardown', true) "
                "RETURNING id"
            )
        )
    ).scalar_one()
    try:
        await db.execute(
            sa_text(
                "INSERT INTO role_permissions (role_id, permission_id) "
                "SELECT :role_id, id FROM permissions WHERE code = 'wagle.messages.read'"
            ),
            {"role_id": role_id},
        )
        await db.commit()
        await _grant_role(db, member.membership_id, "qa_cardinality_extra_reader_001")  # row 3, distinct role

        resp = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=member.headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
    finally:
        await db.execute(sa_text("DELETE FROM membership_role_assignments WHERE role_id = :role_id"), {"role_id": role_id})
        await db.execute(sa_text("DELETE FROM role_permissions WHERE role_id = :role_id"), {"role_id": role_id})
        await db.execute(sa_text("DELETE FROM roles WHERE id = :role_id"), {"role_id": role_id})
        await db.commit()


async def test_single_role_with_permission_still_allowed(family_env):
    """Regression: the untouched single-role path must keep working exactly
    as before this fix."""
    client, family_id = family_env["client"], family_env["family_id"]
    resp = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=family_env["member"].headers)
    assert resp.status_code == 200


async def test_role_without_the_permission_denied(family_env):
    """Has an active membership and an active Wagle subscription, but no
    Wagle role assignment at all -- must still be denied, not granted by
    virtue of merely being a family member."""
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    no_role_actor = await create_actor(db, family_id, name="no-wagle-role", service_role=None)

    resp = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=no_role_actor.headers)
    assert resp.status_code == 403


async def test_no_membership_denied(family_env):
    """A real, valid actor -- but for a different Family than the one in the
    URL -- has no membership row for *this* family at all."""
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    other_family = await create_family(db, "Cardinality Other Family")
    outsider = await create_actor(db, other_family, name="cardinality-outsider", service_role="participant")
    await set_subscription(db, other_family, "active")

    resp = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=outsider.headers)
    assert resp.status_code == 403


async def test_cross_family_duplicate_role_membership_still_scoped_to_its_own_family(family_env):
    """The duplicate-role fix must not leak cross-family: an actor whose
    *own* family membership has 2 READ-granting roles still cannot read a
    *different* family's rooms."""
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    other_family = await create_family(db, "Cardinality Cross Family")
    double_role_elsewhere = await create_actor(db, other_family, name="double-role-elsewhere", service_role="participant")
    await _grant_role(db, double_role_elsewhere.membership_id, "room_admin")
    await set_subscription(db, other_family, "active")

    resp = await client.get(f"/api/families/{family_id}/wagle/rooms", headers=double_role_elsewhere.headers)
    assert resp.status_code == 403
