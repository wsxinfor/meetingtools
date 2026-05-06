import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TranscriptSegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    audio_file_id: uuid.UUID
    segment_index: int
    start_ms: int
    end_ms: int
    speaker_label: str | None
    raw_text: str | None
    corrected_text: str | None
    confidence: float | None
    created_at: datetime
    updated_at: datetime


class TranscriptSegmentUpdate(BaseModel):
    corrected_text: str | None = None
    speaker_label: str | None = None
