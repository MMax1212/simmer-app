"""US2.1 Task 1.1: Category DB schema & migration (Hashtag tags)."""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003_recipe_tools"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create the 'tags' table for hashtag categories
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=True)
    op.create_index("ix_tags_id", "tags", ["id"], unique=False)

    # 2. Create 'recipe_tags' association table
    op.create_table(
        "recipe_tags",
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_recipe_tags_recipe_id", "recipe_tags", ["recipe_id"])
    op.create_index("ix_recipe_tags_tag_id", "recipe_tags", ["tag_id"])


def downgrade() -> None:
    # Drop association table first due to foreign key constraints
    op.drop_index("ix_recipe_tags_tag_id", table_name="recipe_tags")
    op.drop_index("ix_recipe_tags_recipe_id", table_name="recipe_tags")
    op.drop_table("recipe_tags")

    # Drop tags table
    op.drop_index("ix_tags_id", table_name="tags")
    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_table("tags")