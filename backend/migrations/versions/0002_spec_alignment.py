from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    if "admin_audit" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table("admin_audit",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("target_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("before", sa.JSON(), nullable=False),
            sa.Column("after", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("uq_users_username_lower", "users", [sa.text("lower(username)")], unique=True, if_not_exists=True)


def downgrade():
    op.drop_index("uq_users_username_lower", table_name="users")
    op.drop_table("admin_audit")
