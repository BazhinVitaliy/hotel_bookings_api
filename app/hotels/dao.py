from datetime import date, datetime

from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import IncorrectDatesException, PastDatesException
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_hotels_with_unbooked_rooms(
        cls, location: str, date_from: date, date_to: date
    ):
        if date_from >= date_to:
            raise IncorrectDatesException
        if date_from < datetime.now().date():
            raise PastDatesException
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE
            (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
            (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        ),
        hotels_booked_rooms AS (
            SELECT hotel_id, COUNT(*) AS count_booked_rooms
            FROM rooms JOIN booked_rooms ON rooms.id = booked_rooms.room_id
            GROUP BY(hotel_id)
        )
        SELECT name, location, services, rooms_quantity, image_id,
               rooms_quantity - COALESCE(count_booked_rooms, 0) AS rooms_left
        FROM hotels LEFT JOIN hotels_booked_rooms ON hotels.id = hotels_booked_rooms.hotel_id
        WHERE location LIKE '%Алтай%' AND
        rooms_quantity - COALESCE(count_booked_rooms, 0) > 0
        """
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings)
                .where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to,
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from,
                        ),
                    )
                )
                .cte("booked_rooms")
            )

            hotels_booked_rooms = (
                select(Rooms.hotel_id, func.count("*").label("count_booked_rooms"))
                .select_from(Rooms)
                .join(booked_rooms, Rooms.id == booked_rooms.c.room_id)
                .group_by(Rooms.hotel_id)
                .cte("hotels_booked_rooms")
            )

            hotels_with_not_booked_rooms = (
                select(
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (
                        Hotels.rooms_quantity
                        - func.coalesce(hotels_booked_rooms.c.count_booked_rooms, 0)
                    ).label("rooms_left"),
                )
                .select_from(Hotels)
                .join(
                    hotels_booked_rooms,
                    Hotels.id == hotels_booked_rooms.c.hotel_id,
                    isouter=True,
                )
                .where(
                    and_(
                        Hotels.location.like(f"%{location}%"),
                        Hotels.rooms_quantity
                        - func.coalesce(hotels_booked_rooms.c.count_booked_rooms, 0)
                        > 0,
                    )
                )
            )

            result = await session.execute(hotels_with_not_booked_rooms)
            return result.mappings().all()
