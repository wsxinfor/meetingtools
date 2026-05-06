import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(255))
    contact_info: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="customer")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="customer")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str | None] = mapped_column(String(100))
    budget: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="projects")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="project")


class Meeting(Base, TimestampMixin):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    meeting_type: Mapped[str | None] = mapped_column(String(100))
    meeting_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    participants: Mapped[list[str] | None] = mapped_column(JSONB)
    speaker_map: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    raw_text: Mapped[str | None] = mapped_column(Text)
    corrected_text: Mapped[str | None] = mapped_column(Text)
    summary_text: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    customer: Mapped["Customer | None"] = relationship("Customer", back_populates="meetings")
    project: Mapped["Project | None"] = relationship("Project", back_populates="meetings")
