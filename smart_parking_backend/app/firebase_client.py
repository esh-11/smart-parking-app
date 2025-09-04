import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import Config
import os

# Collections (constants)
USERS_COLLECTION = "users"
VEHICLES_COLLECTION = "vehicles"
PARKING_LOTS_COLLECTION = "parking_lots"
BOOKINGS_COLLECTION = "bookings"
PAYMENTS_COLLECTION = "payments"
VERIFICATION_CODES_COLLECTION = "verification_codes"

# Global variables
db = None
firebase_auth = None
firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global db, firebase_auth, firebase_initialized
    
    try:
        if firebase_initialized:
            return True
            
        # Get the service account key path from config
        service_account_path = Config.FIREBASE_SERVICE_ACCOUNT_KEY
        
        # Check if file exists
        if not os.path.exists(service_account_path):
            print(f"❌ Service account file not found: {service_account_path}")
            print("💡 Please make sure you have serviceAccountKey.json in your project root")
            return False
            
        # Initialize with service account key
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        
        # Initialize instances
        db = firestore.client()
        firebase_auth = auth
        firebase_initialized = True
        
        print("✅ Firebase Admin SDK initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Firebase Admin: {e}")
        return False

def get_db():
    """Get Firestore database instance"""
    global db
    if db is None:
        initialize_firebase()
    return db

def get_auth():
    """Get Auth instance"""
    global firebase_auth
    if firebase_auth is None:
        initialize_firebase()
    return firebase_auth

def create_user_with_email_and_password(email, password):
    """Create user using Firebase Admin SDK"""
    try:
        auth_instance = get_auth()
        user = auth_instance.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        return {'localId': user.uid, 'email': user.email}
    except Exception as e:
        raise Exception(f"Failed to create user: {str(e)}")

def sign_in_with_email_and_password(email, password):
    """Sign in user - for testing only"""
    try:
        auth_instance = get_auth()
        # Get user by email to verify they exist
        user = auth_instance.get_user_by_email(email)
        return {
            'localId': user.uid,
            'email': user.email,
            'idToken': 'simulated-for-testing'
        }
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")

# Create firebase_client object
firebase_client = type('obj', (object,), {
    'auth': type('obj', (object,), {
        'create_user_with_email_and_password': create_user_with_email_and_password,
        'sign_in_with_email_and_password': sign_in_with_email_and_password
    })
})

# Initialize Firebase
initialize_firebase()