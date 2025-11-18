from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class UserBase(BaseModel):
    email: str
    full_name: str
    phone: str
    whatsapp: Optional[str] = None
    location: str
    lat: Optional[float] = None
    long: Optional[float] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_provider: bool

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    description: str
    price_gyd: float
    duration_minutes: int

class BookingCreate(BaseModel):
    service_id: int
    start_time: datetime

class PromotionUpdate(BaseModel):
    free_bookings_total: int