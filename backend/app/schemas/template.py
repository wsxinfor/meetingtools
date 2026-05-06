import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class TemplateCreate(BaseModel):
    name: str
    type: str = "general"
    description: str | None = None
    prompt_text: str
    output_schema: dict[str, Any] | None = None
    enabled: bool = True

    @field_validator("name", "prompt_text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("不能为空")
        return v


class TemplateUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    description: str | None = None
    prompt_text: str | None = None
    output_schema: dict[str, Any] | None = None
    enabled: bool | None = None


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    description: str | None
    prompt_text: str
    output_schema: dict[str, Any] | None
    enabled: bool
    owner_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
