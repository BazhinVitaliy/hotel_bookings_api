from datetime import date

from app.bookings.dao import BookingDAO


async def test_add_and_get_booking():
    new_booking = await BookingDAO.add(
        user_id=2,
        room_id=2,
        date_from=date(2023, 7, 10),
        date_to=date(2023, 7, 24)
    )

    assert new_booking.user_id == 2
    assert new_booking.room_id == 2

    id_ = new_booking.id

    result = await BookingDAO.find_by_id(new_booking.id)

    assert result is not None

    await BookingDAO.delete(id=id_)

    result = await BookingDAO.find_by_id(new_booking.id)

    assert result is None
