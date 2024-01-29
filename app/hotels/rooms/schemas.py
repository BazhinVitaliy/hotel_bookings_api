from typing import List

from pydantic import BaseModel, ConfigDict, Json


class SRooms(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: Json[List[str]]
    quantity: int
    image_id: int


class RoomInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
    name: str
    description: str
    services: List[str]
    price: int
    quantity: int
    image_id: int
    total_cost: int
    rooms_left: int
