"""Create user_follows table for social follow network (US3.5 Task 3.5.1)."""
from alembic import op
import sqlalchemy as sa

revision = "0007_user_follows"
down_revision = "0006_completed_recipes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_follows",
        sa.Column("follower_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("following_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("follower_id != following_id", name="ck_user_follows_no_self_follow"),
    )
    op.create_index("ix_user_follows_follower_id", "user_follows", ["follower_id"])
    op.create_index("ix_user_follows_following_id", "user_follows", ["following_id"])


def downgrade():
    op.drop_index("ix_user_follows_following_id", table_name="user_follows")
    op.drop_index("ix_user_follows_follower_id", table_name="user_follows")
    op.drop_table("user_follows")
