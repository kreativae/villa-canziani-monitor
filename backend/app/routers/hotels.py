from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.database import get_db
from app.schemas.hotel import Hotel, HotelCreate, HotelUpdate, HotelWithLatestPrices

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/", response_model=list[HotelWithLatestPrices])
async def list_hotels(active_only: bool = True, db: Client = Depends(get_db)):
    query = db.table("hotels").select("*").order("name")
    if active_only:
        query = query.eq("active", True)
    hotels = query.execute().data

    enriched = []
    for h in hotels:
        latest = _get_latest_prices(db, h["id"])
        enriched.append({**h, **latest})
    return enriched


@router.get("/{hotel_id}", response_model=HotelWithLatestPrices)
async def get_hotel(hotel_id: str, db: Client = Depends(get_db)):
    result = db.table("hotels").select("*").eq("id", hotel_id).single().execute()
    if not result.data:
        raise HTTPException(404, "Hotel not found")
    latest = _get_latest_prices(db, hotel_id)
    return {**result.data, **latest}


@router.post("/", response_model=Hotel, status_code=201)
async def create_hotel(payload: HotelCreate, db: Client = Depends(get_db)):
    result = db.table("hotels").insert(payload.model_dump()).execute()
    return result.data[0]


@router.patch("/{hotel_id}", response_model=Hotel)
async def update_hotel(hotel_id: str, payload: HotelUpdate, db: Client = Depends(get_db)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    result = db.table("hotels").update(data).eq("id", hotel_id).execute()
    if not result.data:
        raise HTTPException(404, "Hotel not found")
    return result.data[0]


@router.delete("/{hotel_id}", status_code=204)
async def delete_hotel(hotel_id: str, db: Client = Depends(get_db)):
    db.table("hotels").update({"active": False}).eq("id", hotel_id).execute()


def _get_latest_prices(db: Client, hotel_id: str) -> dict:
    rows = (
        db.table("price_snapshots")
        .select("source, price, scraped_at")
        .eq("hotel_id", hotel_id)
        .order("scraped_at", desc=True)
        .limit(10)
        .execute()
        .data
    )

    official = next((r for r in rows if r["source"] == "official"), None)
    booking = next((r for r in rows if r["source"] == "booking"), None)

    op = official["price"] if official else None
    bp = booking["price"] if booking else None
    diff_pct = None
    if op and bp:
        diff_pct = round(((bp - op) / op) * 100, 2)

    last = rows[0]["scraped_at"] if rows else None
    return {
        "latest_official_price": op,
        "latest_booking_price": bp,
        "price_diff_pct": diff_pct,
        "last_scraped_at": last,
    }
