"""Create or adopt the original Sprint 1 schema without deleting data."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    expected = {
        "users": {"id", "email", "username", "hashed_password", "role", "is_active", "created_at", "bio", "avatar_url", "dietary_prefs"},
        "recipes": {"id", "owner_id", "title", "description", "instructions", "prep_time_mins", "cook_time_mins", "servings", "created_at", "updated_at"},
        "ingredients": {"id", "recipe_id", "position", "name", "quantity", "unit"},
    }
    found = set(inspector.get_table_names()) & expected.keys()
    if found:
        if found != expected.keys() or any(
            not fields.issubset({c["name"] for c in inspector.get_columns(table)})
            for table, fields in expected.items()
        ):
            raise RuntimeError("Unrecognized existing schema. Back up the database and inspect it before upgrading.")
        return
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("bio", sa.Text()), sa.Column("avatar_url", sa.String(500)),
        sa.Column("dietary_prefs", sa.JSON(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_table("recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("prep_time_mins", sa.Integer()), sa.Column("cook_time_mins", sa.Integer()),
        sa.Column("servings", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_recipes_owner_id", "recipes", ["owner_id"])
    op.create_table("ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("quantity", sa.Float()), sa.Column("unit", sa.String(30)))
    op.create_index("ix_ingredients_recipe_id", "ingredients", ["recipe_id"])


def downgrade():
    op.drop_table("ingredients")
    op.drop_table("recipes")
    op.drop_table("users")
