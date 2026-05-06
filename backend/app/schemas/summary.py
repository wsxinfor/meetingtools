import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SummaryCreate(BaseModel):
    template_id: uuid.UUID
    source: str = "corrected_text"
    llm_config_id: uuid.UUID | None = None


class SummaryUpdate(BaseModel):
    title: str | None = None
    content_md: str | None = None
    is_final: bool | None = None


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    template_id: uuid.UUID | None
    llm_config_id: uuid.UUID | None
    llm_model: str | None
    title: str | None
    content_md: str | None
    content_json: dict[str, Any] | None
    version: int
    is_final: bool
    created_at: datetime
