from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.firebase_client import db, PARKING_LOTS_COLLECTION, BOOKINGS_COLLECTION
from geopy.distance import geodesic
import datetime
from dateutil import parser

bp = Blueprint('parking', __name__)

@bp.route('/lots', methods=['GET'])
def get_parking_lots():
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lng', type=float)
        radius = request.args.get('radius', default=5, type=float)
        
        lots_ref = db.collection(PARKING_LOTS_COLLECTION)
        lots = [doc.to_dict() for doc in lots_ref.stream()]
        
        if latitude and longitude:
            user_location = (latitude, longitude)
            nearby_lots = []
            
            for lot in lots:
                lot_location = (lot['latitude'], lot['longitude'])
                distance = geodesic(user_location, lot_location).km
                
                if distance <= radius:
                    lot['distance'] = round(distance, 2)
                    nearby_lots.append(lot)
                    
            return jsonify(nearby_lots), 200
        
        return jsonify(lots), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/lots/<lot_id>', methods=['GET'])
def get_parking_lot(lot_id):
    try:
        lot_ref = db.collection(PARKING_LOTS_COLLECTION).document(lot_id)
        lot = lot_ref.get()
        
        if not lot.exists:
            return jsonify({'message': 'Parking lot not found'}), 404
            
        return jsonify(lot.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    try:
        user_id = get_jwt_identity()
        bookings_ref = db.collection(BOOKINGS_COLLECTION).where('userId', '==', user_id)
        bookings = [doc.to_dict() for doc in bookings_ref.stream()]
        
        # Sort by creation date (newest first)
        bookings.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return jsonify(bookings), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get parking lot
        lot_ref = db.collection(PARKING_LOTS_COLLECTION).document(data['parkingLotId'])
        lot = lot_ref.get()
        
        if not lot.exists:
            return jsonify({'message': 'Parking lot not found'}), 404
            
        lot_data = lot.to_dict()
        
        if lot_data['availableSpots'] <= 0:
            return jsonify({'message': 'No available spots'}), 400
        
        # Calculate price
        start_time = parser.parse(data['startTime'])
        end_time = parser.parse(data['endTime'])
        duration_hours = (end_time - start_time).total_seconds() / 3600
        total_price = round(duration_hours * lot_data['pricePerHour'], 2)
        
        booking_data = {
            'userId': user_id,
            'parkingLotId': data['parkingLotId'],
            'vehicleId': data['vehicleId'],
            'startTime': data['startTime'],
            'endTime': data['endTime'],
            'totalPrice': total_price,
            'status': 'reserved',
            'createdAt': datetime.datetime.now().isoformat()
        }
        
        # Create booking
        booking_ref = db.collection(BOOKINGS_COLLECTION).document()
        booking_ref.set(booking_data)
        
        # Update available spots
        lot_ref.update({
            'availableSpots': lot_data['availableSpots'] - 1
        })
        
        # Add ID to response
        booking_data['id'] = booking_ref.id
        
        return jsonify(booking_data), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/bookings/<booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify booking belongs to user
        booking_ref = db.collection(BOOKINGS_COLLECTION).document(booking_id)
        booking = booking_ref.get()
        
        if not booking.exists or booking.to_dict().get('userId') != user_id:
            return jsonify({'message': 'Booking not found'}), 404
        
        update_data = {}
        if 'status' in data:
            update_data['status'] = data['status']
            
            # If cancelling, increase available spots
            if data['status'] == 'cancelled':
                lot_id = booking.to_dict().get('parkingLotId')
                lot_ref = db.collection(PARKING_LOTS_COLLECTION).document(lot_id)
                lot = lot_ref.get()
                
                if lot.exists:
                    lot_data = lot.to_dict()
                    lot_ref.update({
                        'availableSpots': lot_data['availableSpots'] + 1
                    })
        
        booking_ref.update(update_data)
        updated_booking = booking_ref.get().to_dict()
        updated_booking['id'] = booking_id
        
        return jsonify(updated_booking), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bp.route('/bookings/<booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify booking belongs to user
        booking_ref = db.collection(BOOKINGS_COLLECTION).document(booking_id)
        booking = booking_ref.get()
        
        if not booking.exists or booking.to_dict().get('userId') != user_id:
            return jsonify({'message': 'Booking not found'}), 404
            
        booking_data = booking.to_dict()
        
        if booking_data['status'] not in ['reserved', 'active']:
            return jsonify({'message': 'Cannot cancel completed or already cancelled booking'}), 400
        
        # Increase available spots
        lot_ref = db.collection(PARKING_LOTS_COLLECTION).document(booking_data['parkingLotId'])
        lot = lot_ref.get()
        
        if lot.exists:
            lot_data = lot.to_dict()
            lot_ref.update({
                'availableSpots': lot_data['availableSpots'] + 1
            })
        
        # Update booking status
        booking_ref.update({'status': 'cancelled'})
        
        return jsonify({'message': 'Booking cancelled successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500