from app import create_app
from extensions import db
from models import User, Airline, Flight
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email='admin@flight.com').first():
        admin = User(username='admin', email='admin@flight.com', role='admin')
        admin.set_password('Admin123!')
        db.session.add(admin)

    if not Airline.query.first():
        airlines = [
            Airline(name='Skyline Airways', country='USA', logo='https://via.placeholder.com/80x40.png?text=Skyline'),
            Airline(name='AeroJet', country='Canada', logo='https://via.placeholder.com/80x40.png?text=AeroJet'),
            Airline(name='Blue Horizon', country='UK', logo='https://via.placeholder.com/80x40.png?text=BlueHorizon'),
        ]
        db.session.add_all(airlines)
        db.session.commit()

        now = datetime.utcnow()
        flights = [
            Flight(flight_number='SKY101', airline_id=airlines[0].id, departure_city='New York', destination_city='Miami', departure_time=now + timedelta(hours=3), arrival_time=now + timedelta(hours=6), status='On Time', gate='A12', duration='3h', price=199.99, available_seats=42),
            Flight(flight_number='AEX230', airline_id=airlines[1].id, departure_city='Toronto', destination_city='Vancouver', departure_time=now + timedelta(hours=7), arrival_time=now + timedelta(hours=12), status='On Time', gate='B4', duration='5h', price=279.99, available_seats=35),
            Flight(flight_number='BLH450', airline_id=airlines[2].id, departure_city='London', destination_city='Paris', departure_time=now + timedelta(days=1, hours=2), arrival_time=now + timedelta(days=1, hours=4), status='On Time', gate='C5', duration='2h', price=149.99, available_seats=24),
        ]
        db.session.add_all(flights)

    db.session.commit()
    print('Database initialized successfully.')
