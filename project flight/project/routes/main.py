from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Flight, Airline, Favorite, Booking
from forms.flight import FlightSearchForm

main_bp = Blueprint('main', __name__, template_folder='../templates')


@main_bp.route('/')
def index():
    form = FlightSearchForm(request.args)
    query = Flight.query.join(Airline)

    if form.departure_city.data:
        query = query.filter(Flight.departure_city.ilike(f"%{form.departure_city.data}%"))
    if form.destination_city.data:
        query = query.filter(Flight.destination_city.ilike(f"%{form.destination_city.data}%"))
    if form.flight_number.data:
        query = query.filter(Flight.flight_number.ilike(f"%{form.flight_number.data}%"))
    if form.airline.data:
        query = query.filter(Airline.name.ilike(f"%{form.airline.data}%"))
    if form.departure_date.data:
        day_start = datetime.combine(form.departure_date.data, datetime.min.time())
        day_end = datetime.combine(form.departure_date.data, datetime.max.time())
        query = query.filter(Flight.departure_time.between(day_start, day_end))

    sort_by = request.args.get('sort_by', 'default')
    if sort_by == 'cheapest':
        query = query.order_by(Flight.price.asc())
    elif sort_by == 'earliest':
        query = query.order_by(Flight.departure_time.asc())
    elif sort_by == 'fastest':
        query = query.order_by(Flight.arrival_time.asc(), Flight.departure_time.asc())
    else:
        query = query.order_by(Flight.departure_time.asc())

    page = request.args.get('page', 1, type=int)
    flights = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('index.html', form=form, flights=flights)


@main_bp.route('/flights')
def flights():
    form = FlightSearchForm(request.args)
    query = Flight.query.join(Airline)

    if form.departure_city.data:
        query = query.filter(Flight.departure_city.ilike(f"%{form.departure_city.data}%"))
    if form.destination_city.data:
        query = query.filter(Flight.destination_city.ilike(f"%{form.destination_city.data}%"))
    if form.flight_number.data:
        query = query.filter(Flight.flight_number.ilike(f"%{form.flight_number.data}%"))
    if form.airline.data:
        query = query.filter(Airline.name.ilike(f"%{form.airline.data}%"))
    if form.departure_date.data:
        day_start = datetime.combine(form.departure_date.data, datetime.min.time())
        day_end = datetime.combine(form.departure_date.data, datetime.max.time())
        query = query.filter(Flight.departure_time.between(day_start, day_end))

    sort_by = request.args.get('sort_by', 'default')
    if sort_by == 'cheapest':
        query = query.order_by(Flight.price.asc())
    elif sort_by == 'earliest':
        query = query.order_by(Flight.departure_time.asc())
    elif sort_by == 'fastest':
        query = query.order_by(Flight.arrival_time.asc(), Flight.departure_time.asc())
    else:
        query = query.order_by(Flight.departure_time.asc())

    page = request.args.get('page', 1, type=int)
    flights_page = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('flights.html', form=form, flights=flights_page)


@main_bp.route('/flight/<int:flight_id>')
def flight_detail(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    return render_template('flight_detail.html', flight=flight)


@main_bp.route('/profile')
@login_required
def profile():
    favorites = current_user.favorites.join(Flight).all()
    bookings = current_user.bookings.order_by(Booking.booking_date.desc()).all()
    return render_template('profile.html', favorites=favorites, bookings=bookings)


@main_bp.route('/favorite/<int:flight_id>', methods=['POST'])
@login_required
def favorite(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    existing = Favorite.query.filter_by(user_id=current_user.id, flight_id=flight.id).first()
    if existing:
        db.session.delete(existing)
        flash('Flight removed from favorites.', 'info')
    else:
        favorite = Favorite(user_id=current_user.id, flight_id=flight.id)
        db.session.add(favorite)
        flash('Flight added to favorites.', 'success')
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))


@main_bp.route('/book/<int:flight_id>', methods=['POST'])
@login_required
def book_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    if flight.available_seats <= 0:
        flash('No seats available for this flight.', 'danger')
        return redirect(url_for('main.flight_detail', flight_id=flight.id))

    # Redirect to payment checkout instead of directly booking
    return redirect(url_for('payment.checkout', flight_id=flight.id))
