from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uuid


class HotelBase(BaseModel):
    name: str
    official_url: Optional[str] = None
    booking_url: Optional[str] = None
    booking_id: Optional[str] = None
    category: Optional[str] = None
    region: str = "Praia do Patacho"
    notes: Optional[str] = None
    engine: Optional[str] = None
    active: bool = True


class HotelCreate(HotelBase):
    pass


class HotelUpdate(HotelBase):
    name: Optional[str] = None
    active: Optional[bool] = None


class Hotel(HotelBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HotelWithLatestPrices(Hotel):
    latest_official_price: Optional[float] = None
    latest_booking_price: Optional[float] = None
    price_diff_pct: Optional[float] = None
    last_scraped_at: Optional[datetime] = None
