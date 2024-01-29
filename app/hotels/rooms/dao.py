from datetime import date

from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def get_free_rooms(
        cls,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT room_id,
            COUNT(*) AS room_bookings
        FROM bookings
        WHERE
        (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        GROUP BY room_id
        )

        SELECT id, hotel_id, name, description,
               services, price, quantity, image_id,
               price * (DATE('2023-06-20') - DATE('2023-05-15')) AS total_cost,
               quantity - COALESCE(room_bookings, 0) AS rooms_left
        FROM rooms LEFT JOIN booked_rooms ON rooms.id = booked_rooms.room_id
        WHERE quantity - COALESCE(room_bookings, 0) > 0 AND
              hotel_id = 1
        """
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings.room_id, func.count("*").label("room_bookings"))
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
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )

            free_rooms = (
                select(
                    Rooms.id,
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                    (Rooms.price * (date_to - date_from).days).label("total_cost"),
                    (
                        Rooms.quantity - func.coalesce(booked_rooms.c.room_bookings, 0)
                    ).label("rooms_left"),
                )
                .select_from(Rooms)
                .join(booked_rooms, Rooms.id == booked_rooms.c.room_id, isouter=True)
                .where(
                    and_(
                        Rooms.quantity - func.coalesce(booked_rooms.c.room_bookings, 0)
                        > 0,
                        Rooms.hotel_id == hotel_id,
                    )
                )
            )

            result = await session.execute(free_rooms)
            return result.mappings().all()
