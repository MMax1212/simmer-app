"""Create saved_posts table for user bookmarks (US3.4.2)."""
from alembic import op
import sqlalchemy as sa

revision = "0008_saved_posts"
down_revision = "0007_user_follows.py"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "saved_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "post_id", name="uq_saved_posts_user_post"),
    )
    op.create_index("ix_saved_posts_user_id", "saved_posts", ["user_id"])
    op.create_index("ix_saved_posts_post_id", "saved_posts", ["post_id"])
def downgrade():
    op.drop_index("ix_saved_posts_post_id", table_name="saved_posts")
    op.drop_index("ix_saved_posts_user_id", table_name="saved_posts")
    op.drop_table("saved_posts")
