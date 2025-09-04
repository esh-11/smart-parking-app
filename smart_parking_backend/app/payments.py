from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List
from app.models import Payment
from app.auth import get_current_active_user
from app.firebase import db

router = APIRouter()

@router.get("/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: str, current_user = Depends(get_current_active_user)):
    payment_ref = db.collection('payments').document(payment_id)
    payment = payment_ref.get()
    
    if not payment.exists:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Get booking to verify user
    booking_ref = db.collection('bookings').document(payment.to_dict()['booking_id'])
    booking = booking_ref.get()
    
    if booking.to_dict()['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    
    return {
        'id': payment.id,
        **payment.to_dict()
    }

@router.post("/payments/{payment_id}/process")
def process_payment(payment_id: str, payment_method: str, current_user = Depends(get_current_active_user)):
    payment_ref = db.collection('payments').document(payment_id)
    payment = payment_ref.get()
    
    if not payment.exists:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_data = payment.to_dict()
    if payment_data['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Payment is not in pending status")
    
    # Get booking to verify user
    booking_ref = db.collection('bookings').document(payment_data['booking_id'])
    booking = booking_ref.get()
    
    if booking.to_dict()['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to process this payment")
    
    # In a real application, you would integrate with a payment gateway here
    # For demo purposes, we'll simulate a successful payment
    transaction_id = f"TRANS_{datetime.utcnow().timestamp()}"  # Demo transaction ID
    
    # Update payment record
    payment_ref.update({
        'status': 'completed',
        'payment_method': payment_method,
        'transaction_id': transaction_id
    })
    
    # Update booking payment status
    booking_ref.update({
        'payment_status': 'completed'
    })
    
    return {
        'payment_id': payment_id,
        'status': 'completed',
        'transaction_id': transaction_id
    }

@router.get("/payments/user/", response_model=List[Payment])
def get_user_payments(current_user = Depends(get_current_active_user)):
    # Get all bookings for the user
    bookings_ref = db.collection('bookings')
    user_bookings = bookings_ref.where('user_id', '==', current_user['id']).get()
    booking_ids = [booking.id for booking in user_bookings]
    
    # Get all payments for these bookings
    payments = []
    for booking_id in booking_ids:
        payments_ref = db.collection('payments')
        booking_payments = payments_ref.where('booking_id', '==', booking_id).get()
        payments.extend([{
            'id': payment.id,
            **payment.to_dict()
        } for payment in booking_payments])
    
    return payments