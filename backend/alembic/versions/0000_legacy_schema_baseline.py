"""Mark the existing init.sql schema as the Alembic baseline.

This revision intentionally creates no legacy table.  Isolated databases that
were initialized by database/init.sql are stamped here before 0001 is applied.
Operating database comparison/stamping remains a Human Gate.
"""

revision = "0000_legacy_schema_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
