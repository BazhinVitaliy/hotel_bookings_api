from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, Query, status
from pydantic import parse_obj_as
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.schemas import BookingsInfo, SBooking
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("")
@version(1)
async def add_booking(
    room_id: int,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking_dict = parse_obj_as(SBooking, booking).dict()
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict


@router.get("")
@version(1)
async def get_bookings_with_info(
    user: Users = Depends(get_current_user),
) -> List[BookingsInfo]:
    return await BookingDAO.get_bookings_with_info_about_rooms(user.id)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
@version(1)
async def delete_booking(
    booking_id: int,
    user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=user.id)
