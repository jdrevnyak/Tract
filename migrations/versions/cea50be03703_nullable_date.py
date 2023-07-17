"""nullable date

Revision ID: cea50be03703
Revises: 5e4aa7b1822f
Create Date: 2023-07-16 19:31:40.858207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cea50be03703'
down_revision = '5e4aa7b1822f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('manual')
    op.drop_table('user')
    op.drop_table('equipment')
    op.drop_table('maintenance_task')
    op.drop_table('role')
    op.drop_table('maintenance_history')
    op.drop_table('roles_users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles_users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('maintenance_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('equipment_id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), nullable=False),
    sa.Column('completed_date', sa.DATETIME(), nullable=False),
    sa.Column('frequency', sa.VARCHAR(length=20), nullable=True),
    sa.Column('occurrence', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), nullable=True),
    sa.Column('permissions', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('maintenance_task',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('equipment_id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), nullable=False),
    sa.Column('next_date', sa.DATETIME(), nullable=False),
    sa.Column('frequency', sa.VARCHAR(length=20), nullable=True),
    sa.Column('occurrence', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), nullable=False),
    sa.Column('room', sa.VARCHAR(length=80), nullable=False),
    sa.Column('barcode', sa.VARCHAR(length=120), nullable=False),
    sa.Column('manual_id', sa.INTEGER(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['manual_id'], ['manual.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('barcode')
    )
    op.create_table('user',
    sa.Column('id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), nullable=True),
    sa.Column('username', sa.VARCHAR(length=255), nullable=False),
    sa.Column('password', sa.VARCHAR(length=255), nullable=False),
    sa.Column('active', sa.BOOLEAN(), nullable=True),
    sa.Column('fs_uniquifier', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('manual',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('url', sa.VARCHAR(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
