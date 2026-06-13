from datetime import datetime
from flask_login import UserMixin
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'


class Airline(db.Model):
    __tablename__ = 'airlines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    logo = db.Column(db.String(255))
    country = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flights = db.relationship('Flight', backref='airline', lazy='dynamic')


class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False, unique=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airlines.id'), nullable=False)
    departure_city = db.Column(db.String(120), nullable=False)
    destination_city = db.Column(db.String(120), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='On Time')
    gate = db.Column(db.String(20))
    duration = db.Column(db.String(30))
    price = db.Column(db.Float, nullable=False)
    available_seats = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='flight', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='flight', lazy='dynamic')


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    seat_number = db.Column(db.String(10))
    status = db.Column(db.String(50), default='Pending')
    payments = db.relationship('Payment', backref='booking', lazy='dynamic')


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50), nullable=False)  # visa, mastercard, debit, mpesa, paypal
    transaction_id = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Completed, Failed, Cancelled
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reference_number = db.Column(db.String(255))
    error_message = db.Column(db.Text)


class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
