from pydantic import BaseModel
from typing import Optional, Any
from datetime import date, datetime
import uuid


class PriceSnapshotBase(BaseModel):
    hotel_id: uuid.UUID
    room_type_id: Optional[uuid.UUID] = None
    source: str                # 'official' | 'booking'
    price: Optional[float] = None
    currency: str = "BRL"
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    guests: int = 2
    breakfast_included: Optional[bool] = None
    cancellation_policy: Optional[str] = None
    availability: Optional[bool] = None
    raw_data: Optional[dict[str, Any]] = None


class PriceSnapshotCreate(PriceSnapshotBase):
    pass


class PriceSnapshot(PriceSnapshotBase):
    id: uuid.UUID
    scraped_at: datetime

    class Config:
        from_attributes = True


class PriceHistory(BaseModel):
    hotel_id: uuid.UUID
    hotel_name: str
    source: str
    snapshots: list[PriceSnapshot]
