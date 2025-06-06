"""Add initial schema

Revision ID: 0139cd0c063e
Revises: 52dbac940d77
Create Date: 2025-04-03 12:27:24.773528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0139cd0c063e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('cognito_id', sa.String(), nullable=False),
    sa.Column('handle', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cognito_id'),
    sa.UniqueConstraint('handle')
    )

    op.create_table('chatbots',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('dialogues',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('questions', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('answer', sa.String(length=255), nullable=False),
    sa.Column('chatbot_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('chatbot_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('file_url', sa.String(), nullable=False),
    sa.Column('sync_msg', sa.String(), nullable=True),
    sa.Column('mime_type', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('sync_status', sa.Enum('NA', 'IN_PROGRESS', 'SYNCED', 'FAILED', name='syncstatus'), nullable=False),
    sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('documents')
    op.execute('DROP TYPE IF EXISTS syncstatus')
    op.drop_table('dialogues')
    op.drop_table('chatbots')
    op.drop_table('users')

    # ### end Alembic commands ###
