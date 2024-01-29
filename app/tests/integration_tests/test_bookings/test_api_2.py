from httpx import AsyncClient


async def test_get_and_delete_bookings(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/bookings")
    assert len(response.json()) == 2

    await authenticated_ac.delete("/bookings/1")
    await authenticated_ac.delete("/bookings/2")

    response = await authenticated_ac.get("/bookings")
    assert len(response.json()) == 0
