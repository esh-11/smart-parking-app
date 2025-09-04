from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config

# Initialize Firebase first
from app.firebase_client import initialize_firebase
initialize_firebase()

jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints with unique names
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.parking import bp as parking_bp
    app.register_blueprint(parking_bp, url_prefix='/parking')
    
    from app.payments import bp as payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')
    
    return app