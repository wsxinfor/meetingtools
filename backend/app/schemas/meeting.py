import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# --- Customer ---

class CustomerCreate(BaseModel):
    name: str
    industry: str | None = None
    contact_info: dict[str, Any] | None = None
    notes: str | None = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    industry: str | None
    contact_info: dict[str, Any] | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


# --- Project ---

class ProjectCreate(BaseModel):
    customer_id: uuid.UUID
    name: str
    stage: str | None = None
    budget: str | None = None
    notes: str | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    name: str
    stage: str | None
    budget: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


# --- Meeting ---

class MeetingCreate(BaseModel):
    title: str
    meeting_type: str | None = None
    customer_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    meeting_time: datetime | None = None
    participants: list[str] | None = None


class MeetingUpdate(BaseModel):
    title: str | None = None
    meeting_type: str | None = None
    customer_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    meeting_time: datetime | None = None
    participants: list[str] | None = None
    status: str | None = None


class MeetingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID | None
    project_id: uuid.UUID | None
    title: str
    meeting_type: str | None
    meeting_time: datetime | None
    participants: list[str] | None
    speaker_map: dict[str, str] | None
    status: str
    created_at: datetime
    updated_at: datetime


class MeetingDetailOut(MeetingOut):
    raw_text: str | None
    corrected_text: str | None
    summary_text: str | None
    error_message: str | None


class SpeakerMapUpdate(BaseModel):
    speaker_map: dict[str, str]


# --- 通用响应 ---

class PagedOut(BaseModel):
    total: int
    items: list[Any]
