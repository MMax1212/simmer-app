"""Create completed_recipes table for cooking history (US2.3)."""
from alembic import op
import sqlalchemy as sa

revision = "0005_completed_recipes"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "completed_recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cooked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_completed_recipes_rating_range"),
    )
    op.create_index("ix_completed_recipes_user_id", "completed_recipes", ["user_id"])
    op.create_index("ix_completed_recipes_recipe_id", "completed_recipes", ["recipe_id"])


def downgrade():
    op.drop_index("ix_completed_recipes_recipe_id", table_name="completed_recipes")
    op.drop_index("ix_completed_recipes_user_id", table_name="completed_recipes")
    op.drop_table("completed_recipes")
