from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, DateTimeLocalField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class FlightSearchForm(FlaskForm):
    departure_city = StringField('Departure city', validators=[Length(max=120)])
    destination_city = StringField('Destination city', validators=[Length(max=120)])
    departure_date = DateField('Date', format='%Y-%m-%d', validators=[], render_kw={'placeholder': 'YYYY-MM-DD'})
    airline = StringField('Airline', validators=[Length(max=120)])
    flight_number = StringField('Flight number', validators=[Length(max=20)])
    sort_by = SelectField('Sort by', choices=[('default', 'Default'), ('cheapest', 'Cheapest'), ('earliest', 'Earliest'), ('fastest', 'Fastest')])
    submit = SubmitField('Search Flights')


class FlightForm(FlaskForm):
    flight_number = StringField('Flight number', validators=[DataRequired(), Length(max=20)])
    airline_id = SelectField('Airline', coerce=int, validators=[DataRequired()])
    departure_city = StringField('Departure city', validators=[DataRequired(), Length(max=120)])
    destination_city = StringField('Destination city', validators=[DataRequired(), Length(max=120)])
    departure_time = DateTimeLocalField('Departure time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    arrival_time = DateTimeLocalField('Arrival time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired(), Length(max=50)])
    gate = StringField('Gate', validators=[Length(max=20)])
    duration = StringField('Duration', validators=[Length(max=30)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    available_seats = IntegerField('Available seats', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Flight')


class AirlineForm(FlaskForm):
    name = StringField('Airline name', validators=[DataRequired(), Length(max=120)])
    country = StringField('Country', validators=[Length(max=120)])
    logo = StringField('Logo URL', validators=[Length(max=255)])
    submit = SubmitField('Save Airline')
