import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AsrConfigCreate(BaseModel):
    name: str
    provider: str = "remote"
    base_url: str = ""
    api_key: str = ""
    enable_diarization: bool = True
    enable_filler_removal: bool = True
    is_default: bool = False
    is_enabled: bool = True

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("不能为空")
        return v.strip()

    @field_validator("base_url")
    @classmethod
    def base_url_required_for_remote(cls, v: str, info) -> str:
        if info.data.get("provider") == "remote" and not v.strip():
            raise ValueError("远程服务必须填写API地址")
        return v.strip()


class AsrConfigUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    enable_diarization: bool | None = None
    enable_filler_removal: bool | None = None
    is_default: bool | None = None
    is_enabled: bool | None = None


class AsrConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    provider: str
    base_url: str
    api_key: str
    enable_diarization: bool
    enable_filler_removal: bool
    is_default: bool
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
