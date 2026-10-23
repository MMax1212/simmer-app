from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    if "users" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table("users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(100), nullable=False),
            sa.Column("username", sa.String(50), nullable=False),
            sa.Column("hashed_password", sa.String(255), nullable=False),
            sa.Column("role", sa.String(20), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
        op.create_index("ix_users_email", "users", ["email"], unique=True)
        op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade():
    op.drop_table("users")
