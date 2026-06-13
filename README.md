# Flight Information Management System

A Flask-based flight information management system with user and admin dashboards, MySQL integration, authentication, search, and CRUD operations.

## Features
- User registration and login
- Flight search by departure, destination, date, airline, and flight number
- Responsive Bootstrap dashboard
- Favorite flights and booking system
- Admin CRUD for flights and airlines
- Booking and user statistics
- MySQL database integration with SQLAlchemy

## Setup
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Create a MySQL database named `flight_management_system` in XAMPP phpMyAdmin.
3. Update `config.py` if your MySQL username or password differ.
4. Initialize the database:
   ```bash
   python database/init_db.py
   ```
5. Run the Flask application:
   ```bash
   python app.py
   ```

## Default Admin
- Email: `admin@flight.com`
- Password: `Admin123!`

## Notes
- Use XAMPP MySQL service and ensure `mysql+pymysql` is installed.
- The app structure includes separate modules for models, forms, routes, and templates.
