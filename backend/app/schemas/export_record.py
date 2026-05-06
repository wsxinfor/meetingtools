import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExportRequest(BaseModel):
    format: str = "docx"


class ExportRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    summary_id: uuid.UUID | None
    export_type: str
    file_format: str
    file_path: str
    created_at: datetime
