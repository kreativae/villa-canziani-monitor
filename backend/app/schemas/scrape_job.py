from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import uuid


class ScrapeJobBase(BaseModel):
    hotel_id: Optional[uuid.UUID] = None
    triggered_by: str = "manual"


class ScrapeJobCreate(ScrapeJobBase):
    pass


class ScrapeJob(ScrapeJobBase):
    id: uuid.UUID
    status: str
    hotels_total: Optional[int] = None
    hotels_done: int = 0
    hotels_failed: int = 0
    error_log: Optional[list[Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
