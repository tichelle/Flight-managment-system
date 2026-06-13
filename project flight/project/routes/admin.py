from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Flight, Airline, Booking
from forms.flight import FlightForm, AirlineForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')


def admin_required():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    if not current_user.is_admin():
        abort(403)


@admin_bp.before_request
def check_admin():
    if request.endpoint and request.endpoint.startswith('admin.'):
        return admin_required()


@admin_bp.route('/')
def dashboard():
    total_flights = Flight.query.count()
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    upcoming = Flight.query.order_by(Flight.departure_time.asc()).limit(5).all()
    sales = db.session.query(db.func.sum(Flight.price)).join(Booking).scalar() or 0
    return render_template('dashboard.html', total_flights=total_flights, total_users=total_users,
                           total_bookings=total_bookings, upcoming=upcoming, sales=sales)


@admin_bp.route('/flights')
def flights():
    page = request.args.get('page', 1, type=int)
    flights = Flight.query.order_by(Flight.departure_time.asc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('flights.html', flights=flights)


@admin_bp.route('/flights/new', methods=['GET', 'POST'])
def new_flight():
    form = FlightForm()
    form.airline_id.choices = [(airline.id, airline.name) for airline in Airline.query.order_by(Airline.name).all()]
    if form.validate_on_submit():
        flight = Flight(
            flight_number=form.flight_number.data,
            airline_id=form.airline_id.data,
            departure_city=form.departure_city.data,
            destination_city=form.destination_city.data,
            departure_time=form.departure_time.data,
            arrival_time=form.arrival_time.data,
            status=form.status.data,
            gate=form.gate.data,
            duration=form.duration.data,
            price=form.price.data,
            available_seats=form.available_seats.data,
        )
        db.session.add(flight)
        db.session.commit()
        flash('Flight created successfully.', 'success')
        return redirect(url_for('admin.flights'))
    return render_template('flight_form.html', form=form, title='Add Flight')


@admin_bp.route('/flights/<int:flight_id>/edit', methods=['GET', 'POST'])
def edit_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    form = FlightForm(obj=flight)
    form.airline_id.choices = [(airline.id, airline.name) for airline in Airline.query.order_by(Airline.name).all()]
    if form.validate_on_submit():
        form.populate_obj(flight)
        db.session.commit()
        flash('Flight updated successfully.', 'success')
        return redirect(url_for('admin.flights'))
    return render_template('flight_form.html', form=form, title='Edit Flight')


@admin_bp.route('/flights/<int:flight_id>/delete', methods=['POST'])
def delete_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    db.session.delete(flight)
    db.session.commit()
    flash('Flight deleted successfully.', 'info')
    return redirect(url_for('admin.flights'))


@admin_bp.route('/airlines')
def airlines():
    airlines = Airline.query.order_by(Airline.name).all()
    return render_template('airlines.html', airlines=airlines)


@admin_bp.route('/airlines/new', methods=['GET', 'POST'])
def new_airline():
    form = AirlineForm()
    if form.validate_on_submit():
        airline = Airline(name=form.name.data, country=form.country.data, logo=form.logo.data)
        db.session.add(airline)
        db.session.commit()
        flash('Airline added successfully.', 'success')
        return redirect(url_for('admin.airlines'))
    return render_template('airline_form.html', form=form, title='Add Airline')


@admin_bp.route('/airlines/<int:airline_id>/edit', methods=['GET', 'POST'])
def edit_airline(airline_id):
    airline = Airline.query.get_or_404(airline_id)
    form = AirlineForm(obj=airline)
    if form.validate_on_submit():
        form.populate_obj(airline)
        db.session.commit()
        flash('Airline updated successfully.', 'success')
        return redirect(url_for('admin.airlines'))
    return render_template('airline_form.html', form=form, title='Edit Airline')


@admin_bp.route('/airlines/<int:airline_id>/delete', methods=['POST'])
def delete_airline(airline_id):
    airline = Airline.query.get_or_404(airline_id)
    db.session.delete(airline)
    db.session.commit()
    flash('Airline deleted successfully.', 'info')
    return redirect(url_for('admin.airlines'))


@admin_bp.route('/users')
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users)


@admin_bp.route('/bookings')
def bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('bookings.html', bookings=bookings)
