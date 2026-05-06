import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AudioFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    original_filename: str
    file_size: int | None
    duration_seconds: float | None
    sample_rate: int | None
    channels: int | None
    status: str
    created_at: datetime
