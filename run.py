#!/usr/bin/env python3
"""
Entry point for the Meeting Room Booking System
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        port=5000,
        reload=True  # Enable auto-reload for development
    ) 