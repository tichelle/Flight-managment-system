#!/usr/bin/env python
"""Database recreation script"""
import sys
import os

# Add the parent directory (project root) to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    from app import create_app
    from extensions import db
    from models import User, Airline, Flight
    from datetime import datetime, timedelta
    import pymysql
    
    # First, create the database
    print("Attempting to connect to MySQL...")
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3306
        )
        cursor = conn.cursor()
        print("Connected to MySQL")
        
        # Drop existing database if it exists
        print("Dropping existing database...")
        cursor.execute("DROP DATABASE IF EXISTS flight_management_system")
        print("Database dropped")
        
        # Create new database
        print("Creating new database...")
        cursor.execute("CREATE DATABASE flight_management_system")
        print("Database created")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        print("Make sure XAMPP MySQL is running!")
        return False
    
    # Now create tables and add data
    print("\nInitializing Flask app...")
    app = create_app()
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created")
        
        # Check if admin exists
        if not User.query.filter_by(email='admin@flight.com').first():
            print("Adding admin user...")
            admin = User(username='admin', email='admin@flight.com', role='admin')
            admin.set_password('Admin123!')
            db.session.add(admin)
            print("Admin user added")
        
        # Check if airlines exist
        if not Airline.query.first():
            print("Adding airlines...")
            airlines = [
                Airline(name='Skyline Airways', country='USA', logo='https://via.placeholder.com/80x40.png?text=Skyline'),
                Airline(name='AeroJet', country='Canada', logo='https://via.placeholder.com/80x40.png?text=AeroJet'),
                Airline(name='Blue Horizon', country='UK', logo='https://via.placeholder.com/80x40.png?text=BlueHorizon'),
            ]
            db.session.add_all(airlines)
            db.session.commit()
            print("Airlines added")
            
            # Add flights
            print("Adding flights...")
            now = datetime.utcnow()
            flights = [
                Flight(flight_number='SKY101', airline_id=airlines[0].id, departure_city='New York', destination_city='Miami', departure_time=now + timedelta(hours=3), arrival_time=now + timedelta(hours=6), status='On Time', gate='A12', duration='3h', price=199.99, available_seats=42),
                Flight(flight_number='AEX230', airline_id=airlines[1].id, departure_city='Toronto', destination_city='Vancouver', departure_time=now + timedelta(hours=7), arrival_time=now + timedelta(hours=12), status='On Time', gate='B4', duration='5h', price=279.99, available_seats=35),
                Flight(flight_number='BLH450', airline_id=airlines[2].id, departure_city='London', destination_city='Paris', departure_time=now + timedelta(days=1, hours=2), arrival_time=now + timedelta(days=1, hours=4), status='On Time', gate='C5', duration='2h', price=149.99, available_seats=24),
                Flight(flight_number='SKY102', airline_id=airlines[0].id, departure_city='Los Angeles', destination_city='New York', departure_time=now + timedelta(hours=5), arrival_time=now + timedelta(hours=12), status='On Time', gate='A5', duration='5h', price=249.99, available_seats=28),
                Flight(flight_number='AEX231', airline_id=airlines[1].id, departure_city='Vancouver', destination_city='Toronto', departure_time=now + timedelta(hours=12), arrival_time=now + timedelta(hours=17), status='On Time', gate='B8', duration='5h', price=259.99, available_seats=45),
            ]
            db.session.add_all(flights)
            print("Flights added")
        
        db.session.commit()
        print("\nDatabase initialized successfully!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
