from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models import Booking, Room, User
from app.schemas import BookingCreate, BookingRead, BookingUpdate, BookingConflictResponse, MessageResponse
from app.auth import get_current_user
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/bookings", response_model=List[BookingRead])
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's bookings"""
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id).all()
    return bookings

@router.get("/bookings/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific booking by ID"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking

@router.post("/bookings", response_model=BookingRead)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new booking"""
    # Check if room exists and is active
    room = db.query(Room).filter(Room.id == booking.room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or inactive"
        )
    
    # Check for booking conflicts
    conflicting_bookings = db.query(Booking).filter(
        and_(
            Booking.room_id == booking.room_id,
            Booking.status == "confirmed",
            or_(
                and_(
                    Booking.start_time <= booking.start_time,
                    Booking.end_time > booking.start_time
                ),
                and_(
                    Booking.start_time < booking.end_time,
                    Booking.end_time >= booking.end_time
                ),
                and_(
                    Booking.start_time >= booking.start_time,
                    Booking.end_time <= booking.end_time
                )
            )
        )
    ).all()
    
    if conflicting_bookings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is already booked for this time slot",
            headers={"X-Conflicting-Bookings": str([b.id for b in conflicting_bookings])}
        )
    
    # Create booking
    db_booking = Booking(
        user_id=current_user.id,
        **booking.dict()
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.put("/bookings/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a booking (only own bookings)"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check for conflicts if updating time
    if booking_update.start_time or booking_update.end_time:
        new_start = booking_update.start_time or booking.start_time
        new_end = booking_update.end_time or booking.end_time
        
        # Additional validation for update duration when only one time is changed
        duration = (new_end - new_start).total_seconds() / 3600
        if duration <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
        if duration > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking cannot exceed 4 hours"
            )
        if duration < 0.5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum booking duration is 30 minutes"
            )
        
        conflicting_bookings = db.query(Booking).filter(
            and_(
                Booking.room_id == booking.room_id,
                Booking.id != booking_id,
                Booking.status == "confirmed",
                or_(
                    and_(
                        Booking.start_time <= new_start,
                        Booking.end_time > new_start
                    ),
                    and_(
                        Booking.start_time < new_end,
                        Booking.end_time >= new_end
                    ),
                    and_(
                        Booking.start_time >= new_start,
                        Booking.end_time <= new_end
                    )
                )
            )
        ).all()
        
        if conflicting_bookings:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room is already booked for this time slot"
            )
    
    # Update booking
    update_data = booking_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/bookings/{booking_id}", response_model=MessageResponse)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking (only own bookings)"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking.status = "cancelled"
    db.commit()
    return MessageResponse(message="Booking cancelled successfully")

@router.get("/rooms/{room_id}/availability")
async def check_room_availability(
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):
    """Check if a room is available for a specific time slot"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check for conflicts
    conflicting_bookings = db.query(Booking).filter(
        and_(
            Booking.room_id == room_id,
            Booking.status == "confirmed",
            or_(
                and_(
                    Booking.start_time <= start_time,
                    Booking.end_time > start_time
                ),
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time >= end_time
                ),
                and_(
                    Booking.start_time >= start_time,
                    Booking.end_time <= end_time
                )
            )
        )
    ).all()
    
    return {
        "available": len(conflicting_bookings) == 0,
        "conflicting_bookings": [BookingRead.from_orm(b) for b in conflicting_bookings]
    } 