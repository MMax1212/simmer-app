"""Seed curated dietary and occasion tags for US4.4 (Task 4.4.1)."""
from alembic import op
import sqlalchemy as sa

revision = "0010_dietary_and_occasion_tag_seeds"
down_revision = "0009_user_follows"
branch_labels = None
depends_on = None

CURATED_DIETARY_TAGS = [
    "#vegan",
    "#vegetarian",
    "#gluten-free",
    "#keto",
    "#low-carb",
    "#dairy-free",
    "#nut-free",
]

CURATED_OCCASION_TAGS = [
    "#quick-dinner",
    "#under-30-mins",
    "#date-night",
    "#meal-prep",
    "#comfort-food",
    "#kid-friendly",
]

ALL_CURATED_TAGS = CURATED_DIETARY_TAGS + CURATED_OCCASION_TAGS


def upgrade() -> None:
    bind = op.get_bind()
    existing_tags = {
        row[0]
        for row in bind.execute(sa.text("SELECT name FROM tags")).fetchall()
    }
    tags_table = sa.table("tags", sa.column("name", sa.String))
    new_tags = [{"name": tag} for tag in ALL_CURATED_TAGS if tag not in existing_tags]
    if new_tags:
        op.bulk_insert(tags_table, new_tags)


def downgrade() -> None:
    bind = op.get_bind()
    tag_placeholders = ", ".join(f":tag_{i}" for i in range(len(ALL_CURATED_TAGS)))
    params = {f"tag_{i}": tag for i, tag in enumerate(ALL_CURATED_TAGS)}
    bind.execute(
        sa.text(
            f"DELETE FROM recipe_tags WHERE tag_id IN (SELECT id FROM tags WHERE name IN ({tag_placeholders}))"
        ),
        params,
    )
    bind.execute(
        sa.text(f"DELETE FROM tags WHERE name IN ({tag_placeholders})"),
        params,
    )
