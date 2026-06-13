# Payment Integration Guide

This Flight Booking application now includes comprehensive payment integration supporting multiple payment methods:
- **Visa Cards** (via Stripe)
- **Mastercard/Debit Cards** (via Stripe)
- **M-Pesa** (Mobile money for Kenya)
- **PayPal** (Global payment processor)

## Setup Instructions

### 1. Install Dependencies

First, update your Python dependencies:

```bash
pip install -r requirements.txt
```

New packages added:
- `stripe>=5.0` - For card payments (Visa/Mastercard)
- `paypal-checkout-sdk>=1.0.1` - For PayPal integration
- `requests>=2.28.0` - For API calls

### 2. Configure Environment Variables

Create a `.env` file in your project root with the following variables:

```env
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_secret
PAYPAL_MODE=sandbox
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_BUSINESS_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
MPESA_ENVIRONMENT=sandbox
```

See `.env.example` for all available options.

## Payment Provider Setup

### Stripe Setup (Visa/Mastercard)

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Sign up for a free account
3. Navigate to **Developers** > **API Keys**
4. Copy your **Publishable Key** and **Secret Key**
5. Add them to your `.env` file:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```

**Test Cards:**
- Visa: `4532 1488 0343 6467`
- Mastercard: `5425 2334 3010 9903`
- Use any future expiry date and any 3-digit CVV

### PayPal Setup

1. Go to [PayPal Developer](https://developer.paypal.com)
2. Sign up and log in
3. Create a sandbox app in **Applications** > **Sandbox Accounts**
4. Get your **Client ID** and **Secret**
5. Add them to your `.env` file:
   ```
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_CLIENT_SECRET=your_secret
   PAYPAL_MODE=sandbox
   ```

### M-Pesa Setup (Kenya Only)

1. Visit [Safaricom Daraja API](https://developer.safaricom.co.ke)
2. Register and create an app
3. Generate credentials for the STK Push service
4. Add them to your `.env` file:
   ```
   MPESA_CONSUMER_KEY=your_key
   MPESA_CONSUMER_SECRET=your_secret
   MPESA_BUSINESS_SHORTCODE=your_shortcode
   MPESA_PASSKEY=your_passkey
   MPESA_ENVIRONMENT=sandbox
   ```

## Database Changes

A new `Payment` model has been added to track all transactions:

```python
class Payment(db.Model):
    id - Payment ID
    booking_id - Associated booking
    user_id - User who made the payment
    amount - Payment amount
    currency - Currency code (USD, KES, etc.)
    payment_method - 'visa', 'mastercard', 'debit', 'mpesa', or 'paypal'
    transaction_id - Unique transaction reference
    status - 'Pending', 'Completed', 'Failed', 'Cancelled'
    payment_date - When payment was made
    reference_number - Payment provider reference
    error_message - Error details if payment failed
```

The `Booking` model has been updated to include:
- Relationship to Payment records
- Status changed to allow 'Pending' status until payment is confirmed

## How Payment Flow Works

### 1. User Initiates Booking
- User clicks "Book Flight" on a flight detail page
- Redirected to payment method selection page
- Selects preferred payment method

### 2. Payment Processing
- **Card Payment**: User enters card details → Payment processed by Stripe → Booking confirmed
- **M-Pesa**: User enters phone number → STK prompt sent → Payment confirmed via callback
- **PayPal**: User redirected to PayPal → Confirms payment → Returned to app

### 3. Booking Confirmation
- Payment record created in database
- Booking status set to "Confirmed"
- Flight available seats reduced by 1
- Success page displayed with booking details

## File Structure

New files created:
```
payment_config.py           - Payment provider configuration
forms/payment.py            - WTForms for payment forms
routes/payment.py           - Payment processing routes
templates/payment/
  ├── checkout.html         - Payment method selection
  ├── card_payment.html     - Card payment form
  ├── card_confirmation.html - Card confirmation
  ├── mpesa_payment.html    - M-Pesa form
  ├── mpesa_confirmation.html - M-Pesa confirmation
  ├── paypal_payment.html   - PayPal form
  └── success.html          - Payment success page
```

Modified files:
- `app.py` - Payment blueprint registered
- `requirements.txt` - Payment libraries added
- `models/__init__.py` - Payment model added, Booking updated
- `routes/main.py` - Book flight route updated to redirect to payment

## Testing Payment Flow

### Test with Stripe (Card)
1. Click "Book Flight"
2. Select "Visa Card" or "Mastercard"
3. Enter test card: `4532 1488 0343 6467`
4. Use any future expiry and any 3-digit CVV
5. Complete payment

### Test with M-Pesa
1. Click "Book Flight"
2. Select "M-Pesa"
3. Enter a Kenyan phone number (will work in sandbox)
4. In sandbox, check the M-Pesa simulator for prompt

### Test with PayPal
1. Click "Book Flight"
2. Select "PayPal"
3. You'll be redirected to PayPal sandbox
4. Log in with your PayPal sandbox account
5. Confirm payment

## Security Considerations

1. **Never** commit `.env` file to version control
2. Use environment variables for all sensitive data
3. Always use HTTPS in production
4. Validate all user inputs server-side
5. Store payment tokens securely
6. Follow PCI DSS compliance guidelines
7. Never store full credit card numbers
8. Use Stripe or PayPal's hosted fields for card data

## Error Handling

All payment endpoints include error handling:
- Invalid payment methods
- Insufficient funds
- Expired cards
- Network errors
- Payment provider errors

Users receive user-friendly error messages and can retry.

## Admin Features

View payment history and booking status in admin dashboard:
- All transactions listed
- Filter by payment method
- View payment details
- Refund capabilities (can be added)

## Troubleshooting

### Stripe Payments Not Working
- Verify API keys in `.env`
- Check Stripe dashboard for errors
- Ensure HTTPS is used in production
- Check browser console for JavaScript errors

### M-Pesa Issues
- Verify Safaricom credentials
- Check callback URL is accessible
- Use sandbox environment for testing
- Ensure phone number format is correct

### PayPal Issues
- Verify Client ID and Secret
- Check PayPal sandbox accounts
- Ensure return URLs are configured correctly
- Verify sandbox mode is enabled

## Deployment to Production

1. **Update `.env` with production keys:**
   ```
   STRIPE_SECRET_KEY=sk_live_...  (production key)
   PAYPAL_MODE=live
   MPESA_ENVIRONMENT=live
   ```

2. **Set HTTPS:**
   - Obtain SSL certificate
   - Configure Flask for HTTPS
   - Update URLs to use https://

3. **Database Migration:**
   ```bash
   flask db upgrade
   ```

4. **Test thoroughly** before going live

## Support & Resources

- [Stripe Documentation](https://stripe.com/docs)
- [PayPal Developer](https://developer.paypal.com)
- [Safaricom Daraja API](https://developer.safaricom.co.ke)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com)

## Next Steps

You can enhance this integration by adding:
- Refund processing
- Payment history reports
- Subscription/recurring payments
- Invoice generation
- Multi-currency support
- Additional payment methods (Apple Pay, Google Pay, etc.)
