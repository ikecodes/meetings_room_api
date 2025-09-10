# Business Configuration
BUSINESS_HOURS = {
    "start": 8,  # 8 AM
    "end": 18,   # 6 PM (18:00)
}

MAX_BOOKING_DURATION_HOURS = 4
MIN_BOOKING_DURATION_HOURS = 0.5  # 30 minutes
BOOKING_ADVANCE_HOURS = 1  # Must book at least 1 hour in advance

ALLOWED_TIME_INTERVALS = [0, 30]  # Only allow bookings at :00 and :30