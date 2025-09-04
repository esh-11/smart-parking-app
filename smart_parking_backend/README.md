# Smart Parking System Backend

This is the backend API for the Smart Parking System, built with FastAPI and Firebase.

## Features

- User authentication and management
- Parking slot management
- Booking system
- Payment processing
- Real-time updates using Firebase

## Prerequisites

- Python 3.8 or higher
- Firebase project (see [Firebase Setup Guide](./FIREBASE_SETUP.md))

## Installation

1. Clone the repository

2. Create and activate a virtual environment (optional but recommended)

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies

   ```bash
   pip install -r venv/requirements.txt
   ```

4. Set up Firebase (see [Firebase Setup Guide](./FIREBASE_SETUP.md))

## Running the Application

1. Initialize the database with sample data (optional)

   ```bash
   python -m app.init_db
   ```

2. Start the server

   ```bash
   python run.py
   ```

   The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /register` - Register a new user
- `POST /token` - Login and get access token

### Parking

- `POST /parking/slots/` - Create a new parking slot
- `GET /parking/slots/` - Get all available parking slots
- `POST /parking/bookings/` - Create a new booking
- `PUT /parking/bookings/{booking_id}/end` - End a booking
- `GET /parking/bookings/user/` - Get all bookings for the current user

### Payments

- `GET /payments/{payment_id}` - Get payment details
- `POST /payments/{payment_id}/process` - Process a payment
- `GET /payments/user/` - Get all payments for the current user

## Project Structure

```
smart_parking_backend/
├── app/
│   ├── __init__.py
│   ├── auth.py          # Authentication logic
│   ├── firebase.py      # Firebase configuration
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── parking.py       # Parking management endpoints
│   └── payments.py      # Payment processing endpoints
├── venv/                # Virtual environment
├── FIREBASE_SETUP.md    # Firebase setup guide
├── README.md            # This file
└── run.py               # Script to run the server
```

## Development

### Adding New Endpoints

To add new endpoints, create a new router in a separate file and include it in `main.py`:

```python
from app import your_module
app.include_router(your_module.router, prefix="/your-prefix", tags=["your-tag"])
```

### Database Schema

The application uses the following Firestore collections:

- `users` - User information
- `parking_slots` - Parking slot information
- `bookings` - Booking information
- `payments` - Payment information

## License

This project is licensed under the MIT License.