from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool = True
    created_at: datetime

class ParkingSlot(BaseModel):
    id: str
    slot_number: str
    floor: str
    is_occupied: bool = False
    vehicle_number: Optional[str] = None
    occupied_since: Optional[datetime] = None

class Booking(BaseModel):
    id: str
    user_id: str
    slot_id: str
    vehicle_number: str
    start_time: datetime
    end_time: Optional[datetime] = None
    amount: float
    status: str  # 'active', 'completed', 'cancelled'
    payment_status: str  # 'pending', 'completed'
    created_at: datetime

class Payment(BaseModel):
    id: str
    booking_id: str
    amount: float
    status: str  # 'pending', 'completed', 'failed'
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime