from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Booking, Room, User
from app.schemas import BookingRead, RoomRead, UserRead, MessageResponse
from app.auth import get_current_admin
from typing import List
from datetime import datetime, date

router = APIRouter()

@router.get("/bookings", response_model=List[BookingRead])
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    room_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Get all bookings with optional filters (Admin only)"""
    query = db.query(Booking)
    
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    
    if start_date:
        query = query.filter(Booking.start_time >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        query = query.filter(Booking.start_time <= datetime.combine(end_date, datetime.max.time()))
    
    bookings = query.offset(skip).limit(limit).all()
    return bookings

@router.get("/bookings/{booking_id}", response_model=BookingRead)
async def get_booking_admin(
    booking_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Get any booking by ID (Admin only)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking

@router.delete("/bookings/{booking_id}", response_model=MessageResponse)
async def cancel_booking_admin(
    booking_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Cancel any booking (Admin only)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking.status = "cancelled"
    db.commit()
    return MessageResponse(message=f"Booking {booking_id} cancelled successfully")

@router.get("/rooms", response_model=List[RoomRead])
async def get_all_rooms_admin(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Get all rooms including inactive ones (Admin only)"""
    query = db.query(Room)
    
    if not include_inactive:
        query = query.filter(Room.is_active == True)
    
    rooms = query.offset(skip).limit(limit).all()
    return rooms

@router.get("/users", response_model=List[UserRead])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Get all users (Admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Get system statistics (Admin only)"""
    total_rooms = db.query(Room).count()
    active_rooms = db.query(Room).filter(Room.is_active == True).count()
    total_bookings = db.query(Booking).count()
    active_bookings = db.query(Booking).filter(Booking.status == "confirmed").count()
    total_users = db.query(User).count()
    
    return {
        "total_rooms": total_rooms,
        "active_rooms": active_rooms,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "total_users": total_users
    }

@router.post("/make-admin/{user_id}")
async def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Make a user an admin (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_superuser = True
    db.commit()
    return MessageResponse(message=f"User {user.email} is now an admin") 