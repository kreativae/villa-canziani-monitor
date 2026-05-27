from fastapi import APIRouter, Depends, Query
from supabase import Client
from app.database import get_db
from app.schemas.price_snapshot import PriceSnapshot
from datetime import date
from typing import Optional

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{hotel_id}", response_model=list[PriceSnapshot])
async def get_price_history(
    hotel_id: str,
    source: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = Query(default=90, le=500),
    db: Client = Depends(get_db),
):
    query = (
        db.table("price_snapshots")
        .select("*")
        .eq("hotel_id", hotel_id)
        .order("scraped_at", desc=True)
        .limit(limit)
    )
    if source:
        query = query.eq("source", source)
    if from_date:
        query = query.gte("scraped_at", from_date.isoformat())
    if to_date:
        query = query.lte("scraped_at", to_date.isoformat())

    return query.execute().data


@router.get("/compare/{hotel_id}")
async def compare_prices(hotel_id: str, db: Client = Depends(get_db)):
    """Return the latest official vs Booking price side-by-side."""
    rows = (
        db.table("price_snapshots")
        .select("source, price, check_in, check_out, scraped_at, breakfast_included, cancellation_policy")
        .eq("hotel_id", hotel_id)
        .order("scraped_at", desc=True)
        .limit(20)
        .execute()
        .data
    )
    official = next((r for r in rows if r["source"] == "official"), None)
    booking = next((r for r in rows if r["source"] == "booking"), None)
    op = official["price"] if official else None
    bp = booking["price"] if booking else None
    diff_pct = round(((bp - op) / op) * 100, 2) if op and bp else None

    return {
        "hotel_id": hotel_id,
        "official": official,
        "booking": booking,
        "diff_pct": diff_pct,
        "cheaper_source": ("official" if (op and bp and op < bp) else "booking") if op and bp else None,
    }
