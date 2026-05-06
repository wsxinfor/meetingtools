import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("用户名不能为空")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码至少6位")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        if v not in ("admin", "user"):
            raise ValueError("角色只能是 admin 或 user")
        return v


class UserUpdate(BaseModel):
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 6:
            raise ValueError("密码至少6位")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in ("admin", "user"):
            raise ValueError("角色只能是 admin 或 user")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
