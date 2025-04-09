"""Add sync fields to dialogue model

Revision ID: 8c51fcae49ce
Revises: e6f5507f9c72
Create Date: 2025-04-09 09:31:23.967481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8c51fcae49ce'
down_revision: Union[str, None] = 'e6f5507f9c72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dialogues', sa.Column('sync_msg', sa.String(), nullable=True))
    op.add_column(
        'dialogues',
        sa.Column(
            'sync_status',
            sa.Enum('NA', 'IN_PROGRESS', 'SYNCED', 'FAILED', name='syncstatus'),
            nullable=False,
            server_default='NA'
        )
    )

    op.create_table(
        'data_chatstore',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('key', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            'value',
            postgresql.ARRAY(postgresql.JSON(astext_type=sa.Text())),
            autoincrement=False,
            nullable=True
        ),
        sa.PrimaryKeyConstraint('id', name='data_chatstore_pkey'),
        sa.UniqueConstraint('key', name='data_chatstore:unique_key')
    )
    op.create_index(
        'data_chatstore:idx_key',
        'data_chatstore',
        ['key'],
        unique=False
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP TYPE IF EXISTS syncstatus")
    op.drop_column('dialogues', 'sync_status')
    op.drop_column('dialogues', 'sync_msg')
    
    op.drop_index('data_chatstore:idx_key', table_name='data_chatstore')
    op.drop_table('data_chatstore')

    # ### end Alembic commands ###
