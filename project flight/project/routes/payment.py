import stripe
import requests
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Booking, Flight, Payment, User
from forms.payment import PaymentForm, CardPaymentForm, MpesaPaymentForm, PayPalPaymentForm
from payment_config import (
    STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET,
    PAYPAL_MODE, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_BUSINESS_SHORTCODE,
    MPESA_PASSKEY, MPESA_ENVIRONMENT, PAYMENT_CURRENCY
)
import base64
import json

payment_bp = Blueprint('payment', __name__, template_folder='../templates', url_prefix='/payment')

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY


@payment_bp.route('/checkout/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def checkout(flight_id):
    """Initial payment method selection"""
    flight = Flight.query.get_or_404(flight_id)
    
    if flight.available_seats <= 0:
        flash('No seats available for this flight.', 'danger')
        return redirect(url_for('main.flight_detail', flight_id=flight.id))
    
    form = PaymentForm()
    
    if form.validate_on_submit():
        # Store flight ID and payment method in session
        session['flight_id'] = flight_id
        session['payment_method'] = form.payment_method.data
        
        if form.payment_method.data == 'visa':
            return redirect(url_for('payment.card_payment', card_type='visa'))
        elif form.payment_method.data == 'mastercard':
            return redirect(url_for('payment.card_payment', card_type='mastercard'))
        elif form.payment_method.data == 'mpesa':
            return redirect(url_for('payment.mpesa_payment'))
        elif form.payment_method.data == 'paypal':
            return redirect(url_for('payment.paypal_payment'))
    
    return render_template('payment/checkout.html', form=form, flight=flight, 
                         stripe_public_key=STRIPE_PUBLIC_KEY)


@payment_bp.route('/card/<card_type>', methods=['GET', 'POST'])
@login_required
def card_payment(card_type):
    """Handle card payments (Visa/Mastercard)"""
    if 'flight_id' not in session:
        flash('Invalid session. Please start over.', 'danger')
        return redirect(url_for('main.flights'))
    
    flight = Flight.query.get_or_404(session['flight_id'])
    form = CardPaymentForm()
    
    if form.validate_on_submit():
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(flight.price * 100),  # Convert to cents
                currency=PAYMENT_CURRENCY.lower(),
                payment_method_types=['card'],
                description=f"Flight booking - {flight.flight_number}",
                metadata={
                    'user_id': current_user.id,
                    'flight_id': flight.id,
                    'card_type': card_type
                }
            )
            
            # Store in session for confirmation
            session['payment_intent_id'] = intent['id']
            session['card_type'] = card_type
            
            return render_template('payment/card_confirmation.html',
                                 flight=flight,
                                 card_last_four=form.card_number.data[-4:],
                                 cardholder_name=form.cardholder_name.data,
                                 card_type=card_type,
                                 payment_intent_id=intent['id'],
                                 client_secret=intent['client_secret'],
                                 stripe_public_key=STRIPE_PUBLIC_KEY)
        
        except stripe.error.CardError as e:
            flash(f"Card declined: {e.message}", 'danger')
            return redirect(url_for('payment.card_payment', card_type=card_type))
        except Exception as e:
            flash(f"Payment error: {str(e)}", 'danger')
            return redirect(url_for('payment.card_payment', card_type=card_type))
    
    return render_template('payment/card_payment.html', form=form, flight=flight, card_type=card_type)


@payment_bp.route('/card/process', methods=['POST'])
@login_required
def process_card_payment():
    """Process card payment with Stripe"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        
        flight = Flight.query.get_or_404(session.get('flight_id'))
        
        # Confirm payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent['status'] == 'succeeded':
            # Create booking
            booking = Booking(
                user_id=current_user.id,
                flight_id=flight.id,
                seat_number=str(flight.available_seats),
                status='Confirmed'
            )
            db.session.add(booking)
            db.session.flush()
            
            # Create payment record
            payment = Payment(
                booking_id=booking.id,
                user_id=current_user.id,
                amount=flight.price,
                currency=PAYMENT_CURRENCY,
                payment_method=session.get('card_type', 'card'),
                transaction_id=payment_intent_id,
                status='Completed',
                reference_number=intent.get('charges')['data'][0]['receipt_number']
            )
            db.session.add(payment)
            
            # Update flight seats
            flight.available_seats -= 1
            db.session.commit()
            
            # Clear session
            session.pop('flight_id', None)
            session.pop('payment_method', None)
            session.pop('payment_intent_id', None)
            
            return jsonify({'success': True, 'booking_id': booking.id})
        
        return jsonify({'success': False, 'error': 'Payment not confirmed'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/mpesa', methods=['GET', 'POST'])
@login_required
def mpesa_payment():
    """Handle M-Pesa payments"""
    if 'flight_id' not in session:
        flash('Invalid session. Please start over.', 'danger')
        return redirect(url_for('main.flights'))
    
    flight = Flight.query.get_or_404(session['flight_id'])
    form = MpesaPaymentForm()
    
    if form.validate_on_submit():
        try:
            phone_number = form.phone_number.data
            # Remove leading 0 and ensure format
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            
            transaction_id = str(uuid.uuid4())
            
            # Initiate M-Pesa STK Push
            mpesa_response = initiate_mpesa_payment(
                phone_number=phone_number,
                amount=int(flight.price),
                transaction_id=transaction_id
            )
            
            if mpesa_response:
                # Create payment record in Pending status
                payment = Payment(
                    user_id=current_user.id,
                    booking_id=None,  # Will be updated after confirmation
                    amount=flight.price,
                    currency='KES',
                    payment_method='mpesa',
                    transaction_id=transaction_id,
                    status='Pending',
                    reference_number=mpesa_response.get('CheckoutRequestID')
                )
                db.session.add(payment)
                db.session.commit()
                
                # Store in session
                session['mpesa_request_id'] = mpesa_response.get('CheckoutRequestID')
                
                flash('M-Pesa prompt sent to your phone. Complete the payment to confirm booking.', 'info')
                return render_template('payment/mpesa_confirmation.html', 
                                     flight=flight,
                                     phone_number=phone_number[-4:],
                                     mpesa_request_id=mpesa_response.get('CheckoutRequestID'))
            else:
                flash('Failed to initiate M-Pesa payment. Try again.', 'danger')
        
        except Exception as e:
            flash(f"M-Pesa error: {str(e)}", 'danger')
    
    return render_template('payment/mpesa_payment.html', form=form, flight=flight)


@payment_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """M-Pesa callback handler"""
    try:
        data = request.get_json()
        result = data.get('Body', {}).get('stkCallback', {})
        
        request_id = result.get('CheckoutRequestID')
        payment = Payment.query.filter_by(reference_number=request_id).first()
        
        if not payment:
            return jsonify({'ResultCode': 1}), 200
        
        result_code = result.get('ResultCode')
        
        if result_code == 0:  # Success
            # Create booking
            flight = Flight.query.get(session.get('flight_id'))
            if flight:
                booking = Booking(
                    user_id=payment.user_id,
                    flight_id=flight.id,
                    seat_number=str(flight.available_seats),
                    status='Confirmed'
                )
                db.session.add(booking)
                db.session.flush()
                
                payment.booking_id = booking.id
                payment.status = 'Completed'
                flight.available_seats -= 1
                db.session.commit()
        else:
            payment.status = 'Failed'
            payment.error_message = result.get('ResultDesc', 'Unknown error')
            db.session.commit()
        
        return jsonify({'ResultCode': 0}), 200
    
    except Exception as e:
        return jsonify({'ResultCode': 1, 'error': str(e)}), 500


@payment_bp.route('/paypal', methods=['GET', 'POST'])
@login_required
def paypal_payment():
    """Handle PayPal payments"""
    if 'flight_id' not in session:
        flash('Invalid session. Please start over.', 'danger')
        return redirect(url_for('main.flights'))
    
    flight = Flight.query.get_or_404(session['flight_id'])
    form = PayPalPaymentForm()
    
    if form.validate_on_submit():
        try:
            # Create PayPal order
            paypal_order = create_paypal_order(
                flight=flight,
                user=current_user
            )
            
            if paypal_order and 'id' in paypal_order:
                # Store order ID in session
                session['paypal_order_id'] = paypal_order['id']
                
                # Redirect to PayPal
                for link in paypal_order['links']:
                    if link['rel'] == 'approve':
                        return redirect(link['href'])
            
            flash('Failed to create PayPal order. Try again.', 'danger')
        
        except Exception as e:
            flash(f"PayPal error: {str(e)}", 'danger')
    
    return render_template('payment/paypal_payment.html', form=form, flight=flight)


@payment_bp.route('/paypal/return', methods=['GET'])
@login_required
def paypal_return():
    """PayPal return endpoint (after user approves)"""
    try:
        order_id = request.args.get('token') or session.get('paypal_order_id')
        
        if not order_id:
            flash('PayPal order not found.', 'danger')
            return redirect(url_for('main.flights'))
        
        # Capture payment
        captured_order = capture_paypal_payment(order_id)
        
        if captured_order and captured_order.get('status') == 'COMPLETED':
            flight = Flight.query.get_or_404(session.get('flight_id'))
            
            # Create booking
            booking = Booking(
                user_id=current_user.id,
                flight_id=flight.id,
                seat_number=str(flight.available_seats),
                status='Confirmed'
            )
            db.session.add(booking)
            db.session.flush()
            
            # Create payment record
            payment = Payment(
                booking_id=booking.id,
                user_id=current_user.id,
                amount=float(captured_order['purchase_units'][0]['amount']['value']),
                currency=captured_order['purchase_units'][0]['amount']['currency_code'],
                payment_method='paypal',
                transaction_id=order_id,
                status='Completed',
                reference_number=order_id
            )
            db.session.add(payment)
            
            # Update flight seats
            flight.available_seats -= 1
            db.session.commit()
            
            # Clear session
            session.pop('flight_id', None)
            session.pop('payment_method', None)
            session.pop('paypal_order_id', None)
            
            flash('Payment successful! Your flight is booked.', 'success')
            return redirect(url_for('main.profile'))
        
        flash('Payment was not completed.', 'danger')
        return redirect(url_for('main.flights'))
    
    except Exception as e:
        flash(f"Error processing PayPal payment: {str(e)}", 'danger')
        return redirect(url_for('main.flights'))


@payment_bp.route('/paypal/cancel', methods=['GET'])
@login_required
def paypal_cancel():
    """PayPal cancel endpoint"""
    flash('PayPal payment was cancelled.', 'warning')
    return redirect(url_for('main.flights'))


@payment_bp.route('/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    """Payment success page"""
    booking = Booking.query.get_or_404(booking_id)
    payment = Payment.query.filter_by(booking_id=booking_id).first()
    
    if booking.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('payment/success.html', booking=booking, payment=payment)


@payment_bp.route('/cancel')
@login_required
def payment_cancel():
    """Generic payment cancellation"""
    flash('Payment was cancelled. Your booking was not completed.', 'warning')
    session.pop('flight_id', None)
    session.pop('payment_method', None)
    return redirect(url_for('main.flights'))


# Helper functions for payment processing

def initiate_mpesa_payment(phone_number, amount, transaction_id):
    """Initiate M-Pesa STK push"""
    try:
        # Get access token
        auth_token = get_mpesa_auth_token()
        
        if not auth_token:
            return None
        
        # Prepare M-Pesa STK Push request
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{MPESA_BUSINESS_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': MPESA_BUSINESS_SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': MPESA_BUSINESS_SHORTCODE,
            'PhoneNumber': phone_number,
            'CallBackURL': url_for('payment.mpesa_callback', _external=True),
            'AccountReference': transaction_id,
            'TransactionDesc': 'Flight booking payment'
        }
        
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest' if MPESA_ENVIRONMENT == 'sandbox' else 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json() if response.status_code == 200 else None
    
    except Exception as e:
        print(f"M-Pesa error: {str(e)}")
        return None


def get_mpesa_auth_token():
    """Get M-Pesa authentication token"""
    try:
        auth_string = f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_bytes}',
            'Content-Type': 'application/json'
        }
        
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials' if MPESA_ENVIRONMENT == 'sandbox' else 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        return None
    
    except Exception as e:
        print(f"Auth token error: {str(e)}")
        return None


def create_paypal_order(flight, user):
    """Create PayPal order"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()}'
        }
        
        base_url = 'https://api-m.sandbox.paypal.com' if PAYPAL_MODE == 'sandbox' else 'https://api-m.paypal.com'
        
        order_data = {
            'intent': 'CAPTURE',
            'purchase_units': [
                {
                    'amount': {
                        'currency_code': PAYMENT_CURRENCY,
                        'value': str(flight.price)
                    },
                    'description': f"Flight booking - {flight.flight_number}"
                }
            ],
            'application_context': {
                'return_url': url_for('payment.paypal_return', _external=True),
                'cancel_url': url_for('payment.paypal_cancel', _external=True)
            }
        }
        
        response = requests.post(
            f'{base_url}/v2/checkout/orders',
            headers=headers,
            json=order_data
        )
        
        return response.json() if response.status_code == 201 else None
    
    except Exception as e:
        print(f"PayPal order error: {str(e)}")
        return None


def capture_paypal_payment(order_id):
    """Capture PayPal payment"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()}'
        }
        
        base_url = 'https://api-m.sandbox.paypal.com' if PAYPAL_MODE == 'sandbox' else 'https://api-m.paypal.com'
        
        response = requests.post(
            f'{base_url}/v2/checkout/orders/{order_id}/capture',
            headers=headers
        )
        
        return response.json() if response.status_code == 201 else None
    
    except Exception as e:
        print(f"PayPal capture error: {str(e)}")
        return None
