from flask import Blueprint, request, jsonify
from app.email_service import send_verification_email, generate_verification_code, store_verification_code, verify_code, cleanup_expired_codes
from app.firebase_client import db, USERS_COLLECTION
import datetime

bp = Blueprint('verification', __name__)

@bp.route('/send-verification', methods=['POST'])
def send_verification():
    """Send verification code to email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Check if user already exists
        user_query = db.collection(USERS_COLLECTION).where('email', '==', email).stream()
        if any(user_query):
            return jsonify({'message': 'User with this email already exists'}), 400
        
        # Generate verification code
        code = generate_verification_code()
        
        # Store code in database
        store_verification_code(email, code)
        
        # Send email (async)
        send_verification_email(email, code)
        
        # Clean up expired codes
        cleanup_expired_codes()
        
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
        
        # Generate new code
        code = generate_verification_code()
        
        # Store new code
        store_verification_code(email, code)
        
        # Send email
        send_verification_email(email, code)
        
        return jsonify({
            'message': 'Verification code resent successfully',
            'email': email,
            'expires_in': '10 minutes'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to resend code: {str(e)}'}), 500