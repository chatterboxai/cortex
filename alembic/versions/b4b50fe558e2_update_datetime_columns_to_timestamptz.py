"""update_datetime_columns_to_timestamptz

Revision ID: b4b50fe558e2
Revises: e4c689408a58
Create Date: 2025-03-27 17:26:25.309955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP


# revision identifiers, used by Alembic.
revision: str = 'b4b50fe558e2'
down_revision: Union[str, None] = 'e4c689408a58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert created_at and updated_at columns to TIMESTAMP WITH TIME ZONE
    op.alter_column('users', 'created_at',
                    type_=TIMESTAMP(timezone=True),
                    postgresql_using='created_at AT TIME ZONE \'UTC\'')
    op.alter_column('users', 'updated_at',
                    type_=TIMESTAMP(timezone=True),
                    postgresql_using='updated_at AT TIME ZONE \'UTC\'')


def downgrade() -> None:
    """Downgrade schema."""
    # Convert back to TIMESTAMP WITHOUT TIME ZONE
    op.alter_column('users', 'created_at',
                    type_=sa.DateTime(),
                    postgresql_using='created_at AT TIME ZONE \'UTC\'')
    op.alter_column('users', 'updated_at',
                    type_=sa.DateTime(),
                    postgresql_using='updated_at AT TIME ZONE \'UTC\'')
