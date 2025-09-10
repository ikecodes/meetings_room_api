from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Room, User
from app.schemas import RoomCreate, RoomRead, RoomUpdate, MessageResponse
from app.auth import verify_token, get_current_user, get_current_admin
from typing import List

router = APIRouter()

@router.get("/rooms", response_model=List[RoomRead])
async def get_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all active rooms - public endpoint"""
    rooms = db.query(Room).filter(Room.is_active == True).offset(skip).limit(limit).all()
    return rooms

@router.get("/rooms/{room_id}", response_model=RoomRead)
async def get_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific room by ID - public endpoint"""
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room

@router.post("/rooms", response_model=RoomRead)
async def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Create a new room (Admin only)"""
    # Check if room name already exists
    existing_room = db.query(Room).filter(Room.name == room.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this name already exists"
        )
    
    db_room = Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.put("/rooms/{room_id}", response_model=RoomRead)
async def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Update a room (Admin only)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if new name conflicts with existing room
    if room_update.name and room_update.name != room.name:
        existing_room = db.query(Room).filter(Room.name == room_update.name).first()
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room with this name already exists"
            )
    
    # Update room fields
    update_data = room_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    return room

@router.delete("/rooms/{room_id}", response_model=MessageResponse)
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Admin only!
):
    """Delete a room (Admin only)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Soft delete by setting is_active to False
    room.is_active = False
    db.commit()
    return MessageResponse(message=f"Room '{room.name}' has been deactivated") 