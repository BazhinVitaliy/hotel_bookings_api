from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

from app.hotels.dao import HotelDAO
from app.hotels.schemas import HotelInfo

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("")
@cache(expire=30)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
) -> List[HotelInfo]:
    return await HotelDAO.get_hotels_with_unbooked_rooms(location, date_from, date_to)


@router.get("/id/{hotel_id}")
async def get_hotel(hotel_id: int):
    return await HotelDAO.find_by_id(hotel_id)
