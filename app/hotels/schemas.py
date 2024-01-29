from typing import List

from pydantic import BaseModel, ConfigDict, Json


class SHotels(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    location: str
    services: Json[List[str]]
    rooms_quantity: int
    image_id: int


class HotelInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: int
    rooms_left: int
