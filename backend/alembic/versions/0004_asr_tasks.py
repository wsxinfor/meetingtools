"""asr_tasks table

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "asr_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "meeting_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "audio_file_id",
            UUID(as_uuid=True),
            sa.ForeignKey("audio_files.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("engine", sa.String(50), nullable=False, server_default="mock"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("progress", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_asr_tasks_meeting_id", "asr_tasks", ["meeting_id"])


def downgrade() -> None:
    op.drop_table("asr_tasks")
