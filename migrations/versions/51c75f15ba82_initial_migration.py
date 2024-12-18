"""Initial migration

Revision ID: 51c75f15ba82
Revises: 
Create Date: 2024-12-19 18:42:56.740901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51c75f15ba82'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacation_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('substitute_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_vacation_request_substitute', 'user', ['substitute_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vacation_request', schema=None) as batch_op:
        batch_op.drop_constraint('fk_vacation_request_substitute', type_='foreignkey')
        batch_op.drop_column('substitute_id')

    # ### end Alembic commands ###
