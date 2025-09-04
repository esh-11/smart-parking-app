# app/init_db.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import uuid
from datetime import datetime

# Path to your Firebase service account key
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "parking-ae69d-firebase-adminsdk-fbsvc-98c14641b7.json")

# Initialize Firebase app if not already initialized
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(cred_path)
    app = firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

def clear_collections():
    """Clear existing collections before adding sample data"""
    collections = ['users', 'parking_slots', 'bookings', 'payments']
    for collection in collections:
        docs = db.collection(collection).limit(100).get()
        for doc in docs:
            doc.reference.delete()
        print(f"Cleared {collection} collection")

def create_sample_users():
    """Create sample users"""
    users = [
        {
            "id": str(uuid.uuid4()),
            "email": "user1@example.com",
            "full_name": "John Doe",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "user2@example.com",
            "full_name": "Jane Smith",
            "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    for user in users:
        user_id = user.pop('id')
        db.collection('users').document(user_id).set(user)
        print(f"Created user: {user['email']}")
    
    return [user['id'] for user in users]

def create_sample_parking_slots():
    """Create sample parking slots"""
    slots = []
    
    # Create 10 slots on floor 1
    for i in range(1, 11):
        slot_id = str(uuid.uuid4())
        slot = {
            "slot_number": f"A{i:02d}",
            "floor": "1",
            "is_occupied": False,
            "vehicle_number": None,
            "occupied_since": None
        }
        db.collection('parking_slots').document(slot_id).set(slot)
        slots.append({"id": slot_id, **slot})
        print(f"Created parking slot: {slot['slot_number']} on floor {slot['floor']}")
    
    # Create 10 slots on floor 2
    for i in range(1, 11):
        slot_id = str(uuid.uuid4())
        slot = {
            "slot_number": f"B{i:02d}",
            "floor": "2",
            "is_occupied": False,
            "vehicle_number": None,
            "occupied_since": None
        }
        db.collection('parking_slots').document(slot_id).set(slot)
        slots.append({"id": slot_id, **slot})
        print(f"Created parking slot: {slot['slot_number']} on floor {slot['floor']}")
    
    return slots

def create_sample_bookings_and_payments(user_ids, slots):
    """Create sample bookings and payments"""
    # Make 2 slots occupied
    occupied_slots = slots[:2]
    
    for i, slot in enumerate(occupied_slots):
        # Create booking
        booking_id = str(uuid.uuid4())
        vehicle_number = f"ABC{1000+i}"
        start_time = datetime.utcnow()
        
        booking = {
            "user_id": user_ids[i % len(user_ids)],
            "slot_id": slot["id"],
            "vehicle_number": vehicle_number,
            "start_time": start_time,
            "end_time": None,
            "amount": 0.0,
            "status": "active",
            "payment_status": "pending",
            "created_at": start_time
        }
        
        db.collection('bookings').document(booking_id).set(booking)
        print(f"Created booking for slot {slot['slot_number']} with vehicle {vehicle_number}")
        
        # Update slot status
        db.collection('parking_slots').document(slot["id"]).update({
            "is_occupied": True,
            "vehicle_number": vehicle_number,
            "occupied_since": start_time
        })
        print(f"Updated slot {slot['slot_number']} as occupied")

    # Create a completed booking with payment
    completed_slot = slots[2]
    booking_id = str(uuid.uuid4())
    vehicle_number = "XYZ9999"
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()
    amount = 15.0  # $15 for 1.5 hours
    
    booking = {
        "user_id": user_ids[0],
        "slot_id": completed_slot["id"],
        "vehicle_number": vehicle_number,
        "start_time": start_time,
        "end_time": end_time,
        "amount": amount,
        "status": "completed",
        "payment_status": "completed",
        "created_at": start_time
    }
    
    db.collection('bookings').document(booking_id).set(booking)
    print(f"Created completed booking for slot {completed_slot['slot_number']}")
    
    # Create payment
    payment_id = str(uuid.uuid4())
    payment = {
        "booking_id": booking_id,
        "amount": amount,
        "status": "completed",
        "payment_method": "credit_card",
        "transaction_id": f"TRANS_{datetime.utcnow().timestamp()}",
        "created_at": end_time
    }
    
    db.collection('payments').document(payment_id).set(payment)
    print(f"Created payment for booking {booking_id}")

def init_db():
    """Initialize the database with sample data"""
    print("Initializing database with sample data...")
    
    # Clear existing data
    clear_collections()
    
    # Create sample data
    user_ids = create_sample_users()
    slots = create_sample_parking_slots()
    create_sample_bookings_and_payments(user_ids, slots)
    
    print("Database initialization completed!")

if __name__ == "__main__":
    init_db()