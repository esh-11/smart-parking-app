# Firebase Setup Guide for Smart Parking System

## Prerequisites

1. A Google account
2. Firebase project (free tier is sufficient to start)

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter a project name (e.g., "Smart Parking System")
4. Follow the setup wizard to complete project creation

## Step 2: Set Up Firestore Database

1. In your Firebase project console, navigate to "Firestore Database" from the left sidebar
2. Click "Create database"
3. Choose "Start in test mode" for development (you'll want to set up proper security rules before production)
4. Select a database location closest to your users
5. Click "Enable"

## Step 3: Generate Service Account Key

1. In your Firebase project console, click the gear icon next to "Project Overview" and select "Project settings"
2. Navigate to the "Service accounts" tab
3. Click "Generate new private key" button for Firebase Admin SDK
4. Save the downloaded JSON file
5. Rename this file to `firebase-admin-key.json`
6. Place this file in the `app` directory of your backend project

## Step 4: Update Firebase Configuration

Ensure the path to your Firebase service account key in `firebase.py` matches the actual filename:

```python
# Path to your Firebase service account key
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "firebase-admin-key.json")  # Make sure this matches your file name
```

## Step 5: Initialize the Database

After setting up Firebase correctly, you can initialize the database with sample data by running:

```bash
python -m app.init_db
```

## Step 6: Run the Backend Server

Start the backend server with:

```bash
python run.py
```

The API will be available at http://localhost:8000, and you can access the interactive API documentation at http://localhost:8000/docs

## Common Issues

### Invalid JWT Token

If you see an error like "Invalid JWT: Token must be a short-lived token (60 minutes) and in a reasonable timeframe", it could be due to:

1. Your computer's clock being out of sync
2. Using an expired service account key
3. Using an incorrect service account key

Solution: Generate a new service account key and ensure your computer's clock is synchronized.

### Connection Issues

If you're having trouble connecting to Firebase, check:

1. Your internet connection
2. Firewall settings that might be blocking the connection
3. That the service account has the necessary permissions

## Firebase Collections Structure

The backend is designed to work with the following Firestore collections:

1. `users` - Stores user information
2. `parking_slots` - Stores information about parking slots
3. `bookings` - Stores booking information
4. `payments` - Stores payment information

These collections will be automatically created when you initialize the database or when the first document is added to each collection.