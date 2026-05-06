"""initial tables

Revision ID: 0001
Revises:
Create Date: 2026-04-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("industry", sa.String(255)),
        sa.Column("contact_info", JSONB),
        sa.Column("notes", sa.Text),
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
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("stage", sa.String(100)),
        sa.Column("budget", sa.String(255)),
        sa.Column("notes", sa.Text),
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
    op.create_index("ix_projects_customer_id", "projects", ["customer_id"])

    op.create_table(
        "meetings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("meeting_type", sa.String(100)),
        sa.Column("meeting_time", sa.DateTime(timezone=True)),
        sa.Column("participants", JSONB),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("raw_text", sa.Text),
        sa.Column("corrected_text", sa.Text),
        sa.Column("summary_text", sa.Text),
        sa.Column("error_message", sa.Text),
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
    op.create_index("ix_meetings_customer_id", "meetings", ["customer_id"])
    op.create_index("ix_meetings_project_id", "meetings", ["project_id"])
    op.create_index("ix_meetings_status", "meetings", ["status"])


def downgrade() -> None:
    op.drop_table("meetings")
    op.drop_table("projects")
    op.drop_table("customers")
