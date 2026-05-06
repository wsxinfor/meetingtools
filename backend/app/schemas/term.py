import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class TermCreate(BaseModel):
    category: str = "common"
    wrong_text: str
    correct_text: str
    aliases: list[str] | None = None
    enabled: bool = True

    @field_validator("wrong_text", "correct_text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("不能为空")
        return v.strip()


class TermUpdate(BaseModel):
    category: str | None = None
    wrong_text: str | None = None
    correct_text: str | None = None
    aliases: list[str] | None = None
    enabled: bool | None = None


class TermOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: str
    wrong_text: str
    correct_text: str
    aliases: list[str] | None
    enabled: bool
    created_at: datetime
