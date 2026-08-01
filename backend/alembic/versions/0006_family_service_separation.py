"""Stop auto-granting Markpoint ServiceAdmin authority to FamilyAdmin roles (D4).

Found by `MONGLE-W1-SCOPED-RBAC-001`'s own separation test, not reported
externally.

The `0001` seed gave the FAMILY-scope `admin` role `markpoint.missions.manage`
and `markpoint.points.adjust` directly, and gave the FAMILY-scope `owner` role
every permission that existed via a `CROSS JOIN`. Both therefore carried
Markpoint *service administration* authority purely by virtue of being a family
role, which the approved D4/D5 contract prohibits: ServiceAdmin authority must
exist only where it has been explicitly assigned, and a FamilyAdmin never
receives it automatically.

Because these two permissions are attached to FAMILY-scope roles,
`effective_permissions()` also granted them without checking the family's
Markpoint `ServiceSubscription` — the subscription gate only applies to
SERVICE-scope roles. So the latent grant additionally bypassed the entitlement
check.

Impact today is nil and this is deliberately verified rather than assumed: no
product code references either permission code (every `/api/missions/*`,
`/api/daily-points/*` etc. route authorizes through the legacy
`require_admin`/`get_current_player` dependencies), so nothing currently reads
these rows. The defect would have become a real privilege escalation at the
Wave 4/5 Markpoint authorization TRANSFORM, when those routes start consulting
permission codes.

Scope note: `markpoint.own.read` on the `member`/`restricted_member` roles is
deliberately left in place. That is self-read, not service administration, and
whether a family role should carry it at all is a D5-B "default access"
question owned by Wave 4 — not something this Wave 1 revision decides.

The correct path to Markpoint administration remains the SERVICE-scope
`markpoint` roles (`mission_manager`, `point_admin`) that `0001` already seeds
and that `assign_role()` gates behind an active ServiceSubscription.
"""
from alembic import op


# Revision ids are stored in alembic_version.version_num, which is
# varchar(32) — keep this at or under 32 characters.
revision = "0006_family_service_separation"
down_revision = "0005_account_credential_session"
branch_labels = None
depends_on = None


_SERVICE_ADMIN_PERMISSIONS = "('markpoint.missions.manage', 'markpoint.points.adjust')"


def upgrade() -> None:
    op.execute(
        f"""
        DELETE FROM role_permissions rp
        USING roles r, permissions p
        WHERE rp.role_id = r.id
          AND rp.permission_id = p.id
          AND r.scope_type = 'FAMILY'
          AND p.code IN {_SERVICE_ADMIN_PERMISSIONS}
        """
    )


def downgrade() -> None:
    # Restores the 0001 seed's original (contract-violating) grants so the
    # revision is reversible. owner and admin are the only FAMILY roles that
    # held them.
    op.execute(
        f"""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r JOIN permissions p ON p.code IN {_SERVICE_ADMIN_PERMISSIONS}
        WHERE r.scope_type = 'FAMILY' AND r.code IN ('owner', 'admin')
        ON CONFLICT DO NOTHING
        """
    )
