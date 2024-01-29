from datetime import date, datetime
from typing import List

from fastapi import Query

from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import RoomInfo
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
) -> List[RoomInfo]:
    return await RoomDAO.get_free_rooms(hotel_id, date_from, date_to)
