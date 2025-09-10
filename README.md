# Meeting Room Booking System

A full-stack meeting room booking system built with FastAPI, SQLAlchemy, PostgreSQL, and Docker.

## Features

### User Authentication

- User registration and login
- JWT-based authentication
- Role-based access control (Regular users and Admins)

### Room Booking

- View available rooms and schedules
- Book rooms for specific date/time (up to 4 hours)
- Prevent double-bookings
- View and cancel own bookings

### Admin Features

- Add/edit/delete rooms
- View all bookings
- Cancel any booking
- System statistics

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Authentication**: fastapi-users with JWT
- **Database**: PostgreSQL with Alembic migrations
- **Deployment**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd fastApi-demo
   ```

2. **Start the services**

   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**

   ```bash
   docker-compose exec app alembic upgrade head
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Local Development

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**

   ```bash
   createdb meeting_rooms
   ```

3. **Set environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/jwt/login` - Login user
- `POST /auth/jwt/logout` - Logout user

### Rooms

- `GET /api/v1/rooms` - List all active rooms
- `GET /api/v1/rooms/{room_id}` - Get room details
- `POST /api/v1/rooms` - Create room (Admin only)
- `PUT /api/v1/rooms/{room_id}` - Update room (Admin only)
- `DELETE /api/v1/rooms/{room_id}` - Delete room (Admin only)

### Bookings

- `GET /api/v1/bookings` - Get my bookings
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings/{booking_id}` - Get booking details
- `PUT /api/v1/bookings/{booking_id}` - Update booking
- `DELETE /api/v1/bookings/{booking_id}` - Cancel booking
- `GET /api/v1/rooms/{room_id}/availability` - Check room availability

### Admin

- `GET /api/v1/admin/bookings` - Get all bookings
- `GET /api/v1/admin/rooms` - Get all rooms (including inactive)
- `GET /api/v1/admin/users` - Get all users
- `GET /api/v1/admin/stats` - Get system statistics

## Database Schema

### Users

- `id`, `email`, `hashed_password`
- `is_active`, `is_superuser`, `is_verified`
- `created_at`, `updated_at`

### Rooms

- `id`, `name`, `description`, `capacity`
- `amenities`, `is_active`
- `created_at`, `updated_at`

### Bookings

- `id`, `user_id`, `room_id`
- `start_time`, `end_time`, `status`
- `created_at`, `updated_at`

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/meeting_rooms
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting

```bash
black .
isort .
```

## Deployment

The application is containerized and ready for deployment with Docker Compose. For production deployment:

1. Update environment variables
2. Use a production PostgreSQL database
3. Set up proper secrets management
4. Configure reverse proxy (Nginx)
5. Set up SSL certificates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
