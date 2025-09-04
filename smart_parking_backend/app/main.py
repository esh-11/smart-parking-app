from flask import Flask
from app.firebase_client import initialize_firebase

# Initialize Firebase first
initialize_firebase()

def create_app():
    app = Flask(__name__)
    
    # Register blueprints with UNIQUE names
    from app.user_auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.parking import bp as parking_bp
    app.register_blueprint(parking_bp, url_prefix='/parking')
    
    from app.payments import bp as payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')
    
    from app.verification import bp as verification_bp
    app.register_blueprint(verification_bp, url_prefix='/auth')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)