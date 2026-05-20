import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AsrTaskCreate(BaseModel):
    audio_file_id: uuid.UUID
    engine: str = "local"
    asr_config_id: uuid.UUID | None = None


class AsrTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    audio_file_id: uuid.UUID
    asr_config_id: uuid.UUID | None
    engine: str
    status: str
    progress: int
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
