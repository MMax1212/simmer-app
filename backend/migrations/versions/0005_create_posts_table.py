"""create posts table"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('caption', sa.Text(), nullable=False),
    sa.Column('image_url', sa.Text(), nullable=False),
    sa.Column('media_type', sa.String(length=20), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_posts_author_id'), ['author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_posts_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_posts_recipe_id'), ['recipe_id'], unique=False)


def downgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_posts_recipe_id'))
        batch_op.drop_index(batch_op.f('ix_posts_created_at'))
        batch_op.drop_index(batch_op.f('ix_posts_author_id'))

    op.drop_table('posts')
