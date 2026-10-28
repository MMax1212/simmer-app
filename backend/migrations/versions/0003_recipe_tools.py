"""Add kitchen tools without rewriting existing recipes or ingredients."""
from alembic import op
import sqlalchemy as sa

revision = "0003_recipe_tools"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("recipe_tools",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(80), nullable=False))
    op.create_index("ix_recipe_tools_recipe_id", "recipe_tools", ["recipe_id"])


def downgrade():
    op.drop_index("ix_recipe_tools_recipe_id", table_name="recipe_tools")
    op.drop_table("recipe_tools")
