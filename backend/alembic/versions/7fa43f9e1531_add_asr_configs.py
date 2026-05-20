"""add_asr_configs

Revision ID: 7fa43f9e1531
Revises: 0009
Create Date: 2026-05-18 12:57:56.663731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '7fa43f9e1531'
down_revision: Union[str, None] = '0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'asr_configs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('base_url', sa.String(500), nullable=False, server_default=''),
        sa.Column('api_key', sa.String(500), nullable=False, server_default=''),
        sa.Column('enable_diarization', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('enable_filler_removal', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.add_column('asr_tasks', sa.Column('asr_config_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'asr_tasks_asr_config_id_fkey',
        'asr_tasks', 'asr_configs',
        ['asr_config_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('asr_tasks_asr_config_id_fkey', 'asr_tasks', type_='foreignkey')
    op.drop_column('asr_tasks', 'asr_config_id')
    op.drop_table('asr_configs')
