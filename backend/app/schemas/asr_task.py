import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AsrTaskCreate(BaseModel):
    audio_file_id: uuid.UUID
    engine: str = "mock"


class AsrTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    audio_file_id: uuid.UUID
    engine: str
    status: str
    progress: int
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
