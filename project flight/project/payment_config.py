import os
from dotenv import load_dotenv

load_dotenv()

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_your_key_here')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_key_here')

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', 'your_paypal_client_id')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', 'your_paypal_secret')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'

# M-Pesa Configuration (Daraja API)
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', 'your_mpesa_key')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'your_mpesa_secret')
MPESA_BUSINESS_SHORTCODE = os.getenv('MPESA_BUSINESS_SHORTCODE', 'your_shortcode')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'your_passkey')
MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')

# General Payment Settings
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY', 'USD')
PAYMENT_SUCCESS_URL = os.getenv('PAYMENT_SUCCESS_URL', 'http://localhost:5000/payment/success')
PAYMENT_CANCEL_URL = os.getenv('PAYMENT_CANCEL_URL', 'http://localhost:5000/payment/cancel')
