import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "location,date_from,date_to,status_code",
    [
        ("Алтай", "2030-05-01", "2030-05-15", 200),
        ("Алтай", "2030-05-01", "2030-04-01", 400),
    ],
)
async def test_get_hotels_by_location_and_time(
    location, date_from, date_to, status_code, ac: AsyncClient
):
    response = await ac.get(
        "/hotels",
        params={"location": location, "date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == status_code
