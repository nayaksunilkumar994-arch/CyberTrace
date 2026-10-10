from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    case_id: UUID
    event_type: str = Field(min_length=1, max_length=50)
    timestamp: datetime
    source: str | None = Field(default=None, max_length=255)
    actor: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=1)
    severity: str = Field(min_length=1, max_length=20)


class EventResponse(BaseModel):
    id: UUID
    case_id: UUID
    event_type: str
    timestamp: datetime
    source: str | None
    actor: str | None
    description: str
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)