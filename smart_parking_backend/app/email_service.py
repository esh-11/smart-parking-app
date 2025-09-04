from flask_mail import Mail, Message
from flask import current_app
import random
import string
from datetime import datetime
from app.firebase_client import get_db
import threading

mail = Mail()

def init_email(app):
    """Initialize email service"""
    mail.init_app(app)

def generate_verification_code(length=6):
    """Generate a random verification code"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email_async(app, recipient_email, code):
    """Send verification email in background thread"""
    with app.app_context():
        try:
            subject = "Your Smart Parking Verification Code"
            body = f"""
            Hello,

            Your verification code for Smart Parking is: {code}

            This code will expire in 10 minutes.

            If you didn't request this code, please ignore this email.

            Best regards,
            Smart Parking Team
            """

            msg = Message(
                subject=subject,
                recipients=[recipient_email],
                body=body
            )

            mail.send(msg)
            print(f"Verification email sent to {recipient_email}")
            
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")

def send_verification_email(recipient_email, code):
    """Send verification email (runs in background thread)"""
    from app import create_app
    app = create_app()
    
    thread = threading.Thread(
        target=send_verification_email_async,
        args=(app, recipient_email, code)
    )
    thread.start()

def store_verification_code(email, code):
    """Store verification code in Firebase with expiry"""
    expiry_time = datetime.now() + current_app.config['VERIFICATION_CODE_EXPIRY']
    
    verification_data = {
        'email': email,
        'code': code,
        'expires_at': expiry_time.isoformat(),
        'created_at': datetime.now().isoformat(),
        'attempts': 0,
        'is_used': False,
        'is_verified': False
    }
    
    # Store in Firebase
    db = get_db()
    db.collection('verification_codes').document(email).set(verification_data)

def verify_code(email, code):
    """Verify if the provided code is valid"""
    try:
        db = get_db()
        # Get verification code document
        doc_ref = db.collection('verification_codes').document(email)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False, "No verification code found for this email"
        
        verification_data = doc.to_dict()
        
        # Check if code is already used
        if verification_data.get('is_used', False):
            return False, "This code has already been used"
        
        # Check if code is expired
        expires_at = datetime.fromisoformat(verification_data['expires_at'])
        if datetime.now() > expires_at:
            return False, "Verification code has expired"
        
        # Check if too many attempts
        if verification_data.get('attempts', 0) >= 5:
            return False, "Too many failed attempts. Please request a new code."
        
        # Check if code matches
        if verification_data['code'] != code:
            # Increment attempt count
            doc_ref.update({'attempts': verification_data.get('attempts', 0) + 1})
            return False, "Invalid verification code"
        
        # Mark code as used and verified
        doc_ref.update({
            'is_used': True,
            'is_verified': True,
            'verified_at': datetime.now().isoformat()
        })
        
        return True, "Verification successful"
        
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def resend_verification_code(email):
    """Resend verification code to email"""
    try:
        # Generate new verification code
        code = generate_verification_code()
        
        # Store new code in database
        store_verification_code(email, code)
        
        # Send email
        send_verification_email(email, code)
        
        return True, "Verification code resent successfully"
        
    except Exception as e:
        return False, f"Failed to resend code: {str(e)}"

def cleanup_expired_codes():
    """Clean up expired verification codes"""
    try:
        db = get_db()
        now = datetime.now().isoformat()
        
        # Query expired codes
        expired_codes = db.collection('verification_codes') \
            .where('expires_at', '<', now) \
            .stream()
        
        for doc in expired_codes:
            doc.reference.delete()
            
        print("Cleaned up expired verification codes")
        
    except Exception as e:
        print(f"Error cleaning up expired codes: {str(e)}")