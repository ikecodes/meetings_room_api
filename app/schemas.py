from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Auth schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

# Room schemas
class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: int
    amenities: Optional[str] = None
    is_active: bool = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    amenities: Optional[str] = None
    is_active: Optional[bool] = None

class RoomRead(RoomBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Booking schemas
class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class BookingBase(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.CONFIRMED

class BookingCreate(BookingBase):
    @validator('start_time')
    def validate_start_time(cls, v):        
        # Validate business hours (8 AM to 6 PM)
        if v.hour < 8 or v.hour >= 18:
            raise ValueError('Bookings must be between 8 AM and 6 PM')
        
        # Validate 30-minute intervals
        if v.minute not in [0, 30]:
            raise ValueError('Bookings must start at 30-minute intervals (e.g., 9:00, 9:30)')
        
        return v

    @validator('end_time')
    def validate_booking_duration(cls, v, values):
        if 'start_time' in values:
            start_time = values['start_time']
            duration = (v - start_time).total_seconds() / 3600  # Convert to hours
            
            if duration <= 0:
                raise ValueError('End time must be after start time')
            if duration > 4:
                raise ValueError('Booking cannot exceed 4 hours')
            
            # Validate end time business hours
            if v.hour > 18 or (v.hour == 18 and v.minute > 0):
                raise ValueError('Bookings must end by 6 PM')
            
            # Validate 30-minute intervals
            if v.minute not in [0, 30]:
                raise ValueError('Bookings must end at 30-minute intervals (e.g., 11:00, 11:30)')
            
            # Minimum 30-minute booking
            if duration < 0.5:
                raise ValueError('Minimum booking duration is 30 minutes')
        
        return v

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    
    @validator('start_time')
    def validate_start_time_update(cls, v):
        if v is not None:
            # Validate business hours
            if v.hour < 8 or v.hour >= 18:
                raise ValueError('Bookings must be between 8 AM and 6 PM')
            
            if v.minute not in [0, 30]:
                raise ValueError('Bookings must start at 30-minute intervals (e.g., 9:00, 9:30)')
        
        return v
    
    @validator('end_time')
    def validate_end_time_update(cls, v, values):
        if v is not None:
            # Validate end time business hours
            if v.hour > 18 or (v.hour == 18 and v.minute > 0):
                raise ValueError('Bookings must end by 6 PM')
            
            if v.minute not in [0, 30]:
                raise ValueError('Bookings must end at 30-minute intervals (e.g., 11:00, 11:30)')
            
            # If start_time is being updated too, validate duration
            if 'start_time' in values and values['start_time'] is not None:
                duration = (v - values['start_time']).total_seconds() / 3600
                if duration <= 0:
                    raise ValueError('End time must be after start time')
                if duration > 4:
                    raise ValueError('Booking cannot exceed 4 hours')
                if duration < 0.5:
                    raise ValueError('Minimum booking duration is 30 minutes')
        
        return v

class BookingRead(BookingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserRead] = None
    room: Optional[RoomRead] = None

# Response schemas
class MessageResponse(BaseModel):
    message: str

class BookingConflictResponse(BaseModel):
    message: str
    conflicting_bookings: List[BookingRead] 