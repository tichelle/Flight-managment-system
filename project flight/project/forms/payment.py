from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, Optional
from wtforms.widgets import html_params


class PaymentForm(FlaskForm):
    """Base payment form"""
    payment_method = SelectField(
        'Payment Method',
        choices=[
            ('visa', 'Visa Card'),
            ('mastercard', 'Mastercard (Debit/Credit)'),
            ('mpesa', 'M-Pesa'),
            ('paypal', 'PayPal')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Proceed to Payment')


class CardPaymentForm(FlaskForm):
    """Form for Visa/Mastercard payments"""
    cardholder_name = StringField(
        'Cardholder Name',
        validators=[DataRequired(), Length(min=3, max=120)]
    )
    card_number = StringField(
        'Card Number',
        validators=[DataRequired(), Regexp(r'^\d{13,19}$', message='Invalid card number')]
    )
    expiry_month = SelectField(
        'Expiry Month',
        choices=[(str(i).zfill(2), f"{i:02d}") for i in range(1, 13)],
        validators=[DataRequired()]
    )
    expiry_year = SelectField(
        'Expiry Year',
        choices=[],
        validators=[DataRequired()]
    )
    cvv = StringField(
        'CVV',
        validators=[DataRequired(), Regexp(r'^\d{3,4}$', message='Invalid CVV')]
    )
    save_card = BooleanField('Save this card for future use')
    submit = SubmitField('Pay Now')

    def __init__(self, *args, **kwargs):
        super(CardPaymentForm, self).__init__(*args, **kwargs)
        # Populate expiry years (current year to 20 years ahead)
        from datetime import datetime
        current_year = datetime.now().year
        self.expiry_year.choices = [(str(year), str(year)) for year in range(current_year, current_year + 21)]


class MpesaPaymentForm(FlaskForm):
    """Form for M-Pesa payments"""
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Regexp(r'^(\+254|0)[17]\d{8}$', message='Invalid Kenyan phone number format (e.g., +254712345678)')
        ]
    )
    submit = SubmitField('Pay with M-Pesa')


class PayPalPaymentForm(FlaskForm):
    """Form for PayPal payments"""
    email = StringField(
        'Email Address',
        validators=[DataRequired()]
    )
    submit = SubmitField('Pay with PayPal')
