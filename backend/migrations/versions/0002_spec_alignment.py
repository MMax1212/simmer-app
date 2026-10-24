"""Align the approved API model and retain existing recipes and measurements."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    old_recipes = bind.execute(sa.text("SELECT id, instructions FROM recipes")).all()
    with op.batch_alter_table("users") as batch:
        batch.alter_column("dietary_prefs", new_column_name="culinary_preferences", existing_type=sa.JSON())
        batch.alter_column("username", type_=sa.String(50), existing_type=sa.String(30))
        batch.alter_column("email", type_=sa.String(100), existing_type=sa.String(255))
        batch.alter_column("avatar_url", type_=sa.String(255), existing_type=sa.String(500))
    # Repair legacy JSON nulls produced by the previous profile endpoint.
    bind.execute(sa.text("UPDATE users SET culinary_preferences = '[]' WHERE culinary_preferences IS NULL OR culinary_preferences = 'null'"))
    bind.execute(sa.text("UPDATE recipes SET prep_time_mins = COALESCE(prep_time_mins, 0), cook_time_mins = COALESCE(cook_time_mins, 0), servings = COALESCE(servings, 1)"))
    op.drop_index("ix_recipes_owner_id", table_name="recipes")
    with op.batch_alter_table("recipes") as batch:
        batch.alter_column("owner_id", new_column_name="author_id", existing_type=sa.Integer())
        batch.alter_column("title", type_=sa.String(150), existing_type=sa.String(120))
        batch.drop_column("instructions")
        batch.add_column(sa.Column("cuisine", sa.String(50)))
        batch.add_column(sa.Column("meal_type", sa.String(50)))
        batch.add_column(sa.Column("difficulty", sa.String(20), nullable=False, server_default="medium"))
        batch.add_column(sa.Column("image_url", sa.String(255)))
        batch.alter_column("prep_time_mins", nullable=False, existing_type=sa.Integer())
        batch.alter_column("cook_time_mins", nullable=False, existing_type=sa.Integer())
        batch.alter_column("servings", nullable=False, existing_type=sa.Integer())
    op.create_index("ix_recipes_author_id", "recipes", ["author_id"])
    op.create_index("ix_recipes_title", "recipes", ["title"])
    op.drop_index("ix_ingredients_recipe_id", table_name="ingredients")
    with op.batch_alter_table("ingredients", naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    }) as batch:
        batch.alter_column("quantity", new_column_name="amount", existing_type=sa.Float())
        batch.alter_column("name", type_=sa.String(100), existing_type=sa.String(120))
        batch.drop_constraint("fk_ingredients_recipe_id_recipes", type_="foreignkey")
        batch.create_foreign_key("fk_ingredients_recipe_id_recipes", "recipes", ["recipe_id"], ["id"], ondelete="CASCADE")
    op.rename_table("ingredients", "recipe_ingredients")
    op.create_index("ix_recipe_ingredients_recipe_id", "recipe_ingredients", ["recipe_id"])
    steps = op.create_table("recipe_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.UniqueConstraint("recipe_id", "step_number", name="uq_recipe_step_number"))
    op.create_index("ix_recipe_steps_recipe_id", "recipe_steps", ["recipe_id"])
    for recipe_id, instructions in old_recipes:
        # Keep existing instruction text verbatim; line order defines step order.
        lines = [line for line in instructions.splitlines() if line.strip()] or [instructions]
        op.bulk_insert(steps, [{"recipe_id": recipe_id, "step_number": i, "instruction": line}
                              for i, line in enumerate(lines, 1)])
    op.create_table("admin_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("before", sa.JSON(), nullable=False),
        sa.Column("after", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))

    op.create_index("uq_users_username_lower", "users", [sa.text("lower(username)")], unique=True)


def downgrade():
    raise RuntimeError("This data-preserving upgrade is forward-only. Restore a pre-upgrade backup to roll back.")
