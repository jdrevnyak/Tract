"""trying to add user to maintenance historyyss

Revision ID: 2005a9b1fa3d
Revises: 4d48f145a0b6
Create Date: 2023-07-21 19:45:22.644345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2005a9b1fa3d'
down_revision = '4d48f145a0b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(length=36), nullable=True))
        batch_op.create_foreign_key('fk_user_id', 'user', ['user_id'], ['id'])
        batch_op.drop_column('user')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user', sa.VARCHAR(length=200), nullable=False))
        batch_op.drop_constraint('fk_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
