import uuid

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class TermDictionary(Base):
    __tablename__ = "term_dictionary"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="common")
    wrong_text: Mapped[str] = mapped_column(String(500), nullable=False)
    correct_text: Mapped[str] = mapped_column(String(500), nullable=False)
    aliases: Mapped[list[str] | None] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
