from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.firebase_client import db, USERS_COLLECTION
from app.email_service import send_verification_email, verify_code, resend_verification_code
import datetime
import bcrypt

bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['email', 'password', 'fullName']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        users_ref = db.collection(USERS_COLLECTION).where('email', '==', data['email'])
        if len(list(users_ref.stream())) > 0:
            return jsonify({'message': 'User with this email already exists'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_data = {
            'email': data['email'],
            'password': hashed_password.decode('utf-8'),
            'fullName': data['fullName'],
            'phone': data.get('phone', ''),
            'vehicle': data.get('vehicle', ''),
            'isVerified': False,
            'createdAt': datetime.datetime.now().isoformat()
        }
        
        user_ref = db.collection(USERS_COLLECTION).document()
        user_ref.set(user_data)
        
        # Send verification email
        send_verification_email(data['email'])
        
        return jsonify({
            'message': 'User registered successfully. Verification code sent to email.',
            'userId': user_ref.id
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        
        if 'email' not in data or 'code' not in data:
            return jsonify({'message': 'Email and verification code are required'}), 400
        
        # Verify code
        if verify_code(data['email'], data['code']):
            # Update user verification status
            users_ref = db.collection(USERS_COLLECTION).where('email', '==', data['email'])
            users = list(users_ref.stream())
            
            if len(users) == 0:
                return jsonify({'message': 'User not found'}), 404
            
            user_ref = users[0].reference
            user_ref.update({'isVerified': True})
            
            # Create access token
            access_token = create_access_token(identity=user_ref.id)
            
            return jsonify({
                'message': 'Email verified successfully',
                'token': access_token
            }), 200
        else:
            return jsonify({'message': 'Invalid or expired verification code'}), 400
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'message': 'Email is required'}), 400
        
        # Check if user exists
        users_ref = db.collection(USERS_COLLECTION).where('email', '==', data['email'])
        users = list(users_ref.stream())
        
        if len(users) == 0:
            return jsonify({'message': 'User not found'}), 404
        
        user_data = users[0].to_dict()
        
        # Check if already verified
        if user_data.get('isVerified', False):
            return jsonify({'message': 'Email is already verified'}), 400
        
        # Resend verification code
        result = resend_verification_code(data['email'])
        
        return jsonify({
            'message': 'Verification code resent successfully',
            'email': result['email']
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        users_ref = db.collection(USERS_COLLECTION).where('email', '==', data['email'])
        users = list(users_ref.stream())
        
        if len(users) == 0:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        user = users[0]
        user_data = user.to_dict()
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user_data['password'].encode('utf-8')):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check if verified
        if not user_data.get('isVerified', False):
            # Send verification code
            send_verification_email(data['email'])
            
            return jsonify({
                'message': 'Email not verified. Verification code sent.',
                'verified': False,
                'email': data['email']
            }), 200
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'verified': True
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user_ref = db.collection(USERS_COLLECTION).document(user_id)
        user = user_ref.get()
        
        if not user.exists:
            return jsonify({'message': 'User not found'}), 404
        
        user_data = user.to_dict()
        
        # Remove sensitive information
        if 'password' in user_data:
            del user_data['password']
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_ref = db.collection(USERS_COLLECTION).document(user_id)
        user = user_ref.get()
        
        if not user.exists:
            return jsonify({'message': 'User not found'}), 404
        
        # Fields that can be updated
        allowed_fields = ['fullName', 'phone', 'vehicle']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            user_ref.update(update_data)
        
        # Get updated user data
        updated_user = user_ref.get().to_dict()
        
        # Remove sensitive information
        if 'password' in updated_user:
            del updated_user['password']
        
        return jsonify(updated_user), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500