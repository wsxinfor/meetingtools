import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class LlmConfigCreate(BaseModel):
    name: str
    provider: str = "ollama"
    base_url: str
    api_key: str = ""
    model_name: str
    is_default: bool = False
    is_enabled: bool = True

    @field_validator("name", "base_url", "model_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("不能为空")
        return v.strip()


class LlmConfigUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None
    is_default: bool | None = None
    is_enabled: bool | None = None


class LlmConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    provider: str
    base_url: str
    api_key: str
    model_name: str
    is_default: bool
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
