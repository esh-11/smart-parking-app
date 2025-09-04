from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.firebase_client import get_db, firebase_client, USERS_COLLECTION, VEHICLES_COLLECTION
from app.email_service import send_verification_email, generate_verification_code, store_verification_code, verify_code, resend_verification_code
import datetime

bp = Blueprint('auth', __name__)

def check_email_verification(email):
    """Check if email has been verified through our verification system"""
    try:
        db = get_db()
        # Check if verification code exists and is verified
        verification_ref = db.collection('verification_codes').document(email)
        verification_doc = verification_ref.get()
        
        if not verification_doc.exists:
            return False
        
        verification_data = verification_doc.to_dict()
        return verification_data.get('is_verified', False)
        
    except Exception as e:
        print(f"Error checking email verification: {str(e)}")
        return False

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        db = get_db()
        
        # Check if user already exists
        user_query = db.collection(USERS_COLLECTION).where('email', '==', data['email']).stream()
        if any(user_query):
            return jsonify({'message': 'User with this email already exists'}), 400
        
        # Check if username already exists
        username_query = db.collection(USERS_COLLECTION).where('username', '==', data['username']).stream()
        if any(username_query):
            return jsonify({'message': 'Username already taken'}), 400
        
        # Check if email is verified
        email = data['email']
        is_verified = check_email_verification(email)
        
        if not is_verified:
            return jsonify({
                'message': 'Email not verified. Please verify your email first.',
                'needs_verification': True,
                'email': email
            }), 400

        # Create user using Firebase
        try:
            user = firebase_client.auth.create_user_with_email_and_password(data['email'], data['password'])
            
            # Create user document in Firestore
            user_data = {
                'uid': user['localId'],
                'username': data['username'],
                'email': data['email'],
                'phone': data.get('phone', ''),
                'totalBookings': 0,
                'savedSpots': 0,
                'points': 0,
                'createdAt': datetime.datetime.now().isoformat(),
                'lastUpdated': datetime.datetime.now().isoformat(),
                'emailVerified': False
            }
            
            db.collection(USERS_COLLECTION).document(user['localId']).set(user_data)
            
            # Create access token
            access_token = create_access_token(identity=user['localId'])
            
            return jsonify({
                'message': 'User created successfully',
                'access_token': access_token,
                'user': user_data
            }), 201
            
        except Exception as e:
            error_msg = str(e)
            if 'EMAIL_EXISTS' in error_msg:
                return jsonify({'message': 'Email already exists'}), 400
            elif 'WEAK_PASSWORD' in error_msg:
                return jsonify({'message': 'Password is too weak'}), 400
            else:
                return jsonify({'message': f'Registration failed: {error_msg}'}), 500
        
    except Exception as e:
        return jsonify({'message': f'Registration error: {str(e)}'}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Authenticate with Firebase
        try:
            user = firebase_client.auth.sign_in_with_email_and_password(data['email'], data['password'])
            
            db = get_db()
            # Get user data from Firestore
            user_doc = db.collection(USERS_COLLECTION).document(user['localId']).get()
            
            if not user_doc.exists:
                return jsonify({'message': 'User not found'}), 404
                
            user_data = user_doc.to_dict()
            
            # Create access token
            access_token = create_access_token(identity=user['localId'])
            
            return jsonify({
                'access_token': access_token,
                'user': user_data
            }), 200
            
        except Exception as e:
            error_msg = str(e)
            if 'USER_NOT_FOUND' in error_msg or 'INVALID_EMAIL' in error_msg:
                return jsonify({'message': 'Invalid email address'}), 400
            elif 'INVALID_PASSWORD' in error_msg:
                return jsonify({'message': 'Invalid password'}), 401
            else:
                return jsonify({'message': f'Login failed: {error_msg}'}), 500
        
    except Exception as e:
        return jsonify({'message': f'Login error: {str(e)}'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        db = get_db()
        user_doc = db.collection(USERS_COLLECTION).document(user_id).get()
        
        if not user_doc.exists:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify(user_doc.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    try:
        user_id = get_jwt_identity()
        db = get_db()
        vehicles_ref = db.collection(VEHICLES_COLLECTION).where('userId', '==', user_id)
        vehicles = [doc.to_dict() for doc in vehicles_ref.stream()]
        
        return jsonify(vehicles), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/vehicles', methods=['POST'])
@jwt_required()
def add_vehicle():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['licensePlate', 'make', 'model', 'color']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        db = get_db()
        
        # Check if vehicle already exists for this user
        existing_vehicle = db.collection(VEHICLES_COLLECTION)\
            .where('userId', '==', user_id)\
            .where('licensePlate', '==', data['licensePlate'])\
            .stream()
        
        if any(existing_vehicle):
            return jsonify({'message': 'Vehicle with this license plate already exists'}), 400
        
        vehicle_data = {
            'userId': user_id,
            'licensePlate': data['licensePlate'],
            'make': data['make'],
            'model': data['model'],
            'color': data['color'],
            'createdAt': datetime.datetime.now().isoformat()
        }
        
        # Add vehicle to Firestore
        vehicle_ref = db.collection(VEHICLES_COLLECTION).document()
        vehicle_ref.set(vehicle_data)
        
        # Add ID to response
        vehicle_data['id'] = vehicle_ref.id
        
        return jsonify(vehicle_data), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/vehicles/<vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        # Verify vehicle belongs to user
        vehicle_ref = db.collection(VEHICLES_COLLECTION).document(vehicle_id)
        vehicle = vehicle_ref.get()
        
        if not vehicle.exists or vehicle.to_dict().get('userId') != user_id:
            return jsonify({'message': 'Vehicle not found'}), 404
            
        vehicle_ref.delete()
        
        return jsonify({'message': 'Vehicle deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/send-verification', methods=['POST'])
def send_verification():
    """Send verification code to email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Generate verification code
        code = generate_verification_code()
        
        # Store code in database
        store_verification_code(email, code)
        
        # Send email (async)
        send_verification_email(email, code)
        
        return jsonify({
            'message': 'Verification code sent successfully',
            'email': email,
            'expires_in': '10 minutes'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to send verification code: {str(e)}'}), 500

@bp.route('/verify-code', methods=['POST'])
def verify_verification_code():
    """Verify the provided code"""
    try:
        data = request.get_json()
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return jsonify({'message': 'Email and code are required'}), 400
        
        # Verify the code
        is_valid, message = verify_code(email, code)
        
        if is_valid:
            return jsonify({
                'message': message,
                'verified': True
            }), 200
        else:
            return jsonify({
                'message': message,
                'verified': False
            }), 400
            
    except Exception as e:
        return jsonify({'message': f'Verification failed: {str(e)}'}), 500

@bp.route('/resend-code', methods=['POST'])
def resend_verification_code():
    """Resend verification code"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Resend code using email service
        success, message = resend_verification_code(email)
        
        if success:
            return jsonify({
                'message': message,
                'email': email,
                'expires_in': '10 minutes'
            }), 200
        else:
            return jsonify({'message': message}), 400
        
    except Exception as e:
        return jsonify({'message': f'Failed to resend code: {str(e)}'}), 500