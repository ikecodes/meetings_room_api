from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models import User, Room, Booking
from app.schemas import *
from app.auth import verify_token, create_access_token, get_current_user, get_password_hash, verify_password
from app.routers import rooms, bookings, admin
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="Meeting Room Booking System",
    description="A full-stack meeting room booking system with user authentication and admin controls",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rooms.router, prefix="/api/v1", tags=["rooms"])
app.include_router(bookings.router, prefix="/api/v1", tags=["bookings"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# Custom authentication endpoints
@app.post("/auth/register")
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user with hashed password"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,  # Now properly hashed!
        is_active=True,
        is_superuser=user_data.is_admin,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully", 
        "user_id": new_user.id, 
        "is_admin": user_data.is_admin,
        "email": user_data.email
    }

@app.post("/auth/login")
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user with password verification"""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):  # Proper password verification!
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_email": user.email,
        "is_admin": user.is_superuser
    }

@app.get("/users/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_superuser,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Meeting Room Booking System!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Meeting Room Booking System"}

# Test protected endpoint
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}, this is a protected route!"}