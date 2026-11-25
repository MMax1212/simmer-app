"""Create grocery_lists and grocery_items tables for US4.2 (Task 4.2.2)."""
from alembic import op
import sqlalchemy as sa

revision = "0011_grocery_lists_and_items"
down_revision = "0010_dietary_and_occasion_tag_seeds"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "grocery_lists",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=100),
            nullable=False,
            server_default="My Grocery List",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_grocery_lists_user_id", "grocery_lists", ["user_id"])

    op.create_table(
        "grocery_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "grocery_list_id",
            sa.Integer(),
            sa.ForeignKey("grocery_lists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column(
            "department",
            sa.String(length=50),
            nullable=False,
            server_default="Other",
        ),
        sa.Column(
            "is_checked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "source_recipe_id",
            sa.Integer(),
            sa.ForeignKey("recipes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("amount > 0", name="ck_grocery_items_amount_positive"),
    )
    op.create_index("ix_grocery_items_grocery_list_id", "grocery_items", ["grocery_list_id"])
    op.create_index("ix_grocery_items_name", "grocery_items", ["name"])
    op.create_index("ix_grocery_items_department", "grocery_items", ["department"])
    op.create_index("ix_grocery_items_source_recipe_id", "grocery_items", ["source_recipe_id"])


def downgrade() -> None:
    op.drop_index("ix_grocery_items_source_recipe_id", table_name="grocery_items")
    op.drop_index("ix_grocery_items_department", table_name="grocery_items")
    op.drop_index("ix_grocery_items_name", table_name="grocery_items")
    op.drop_index("ix_grocery_items_grocery_list_id", table_name="grocery_items")
    op.drop_table("grocery_items")

    op.drop_index("ix_grocery_lists_user_id", table_name="grocery_lists")
    op.drop_table("grocery_lists")
