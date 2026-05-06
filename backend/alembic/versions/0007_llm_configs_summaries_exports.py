"""llm_configs, meeting_summaries, export_records tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "llm_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("api_key", sa.String(500), nullable=False, server_default=""),
        sa.Column("model_name", sa.String(255), nullable=False),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "meeting_summaries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "meeting_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "template_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meeting_templates.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "llm_config_id",
            UUID(as_uuid=True),
            sa.ForeignKey("llm_configs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("llm_model", sa.String(255)),
        sa.Column("title", sa.String(500)),
        sa.Column("content_md", sa.Text),
        sa.Column("content_json", JSONB),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_final", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_meeting_summaries_meeting_id", "meeting_summaries", ["meeting_id"])

    op.create_table(
        "export_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "meeting_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "summary_id",
            UUID(as_uuid=True),
            sa.ForeignKey("meeting_summaries.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("export_type", sa.String(50), nullable=False),
        sa.Column("file_format", sa.String(20), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_export_records_meeting_id", "export_records", ["meeting_id"])


def downgrade() -> None:
    op.drop_table("export_records")
    op.drop_table("meeting_summaries")
    op.drop_table("llm_configs")
