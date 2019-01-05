from flask import render_template, flash, redirect, jsonify
from app import app
from app.forms import CarRegistrationForm
from app.models import Car, TrackState

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='Home')

@app.route('/cars')
def cars():
  cars = Car.query.all()
  app.logger.info('got cars:' + repr(cars))
  return render_template('cars.html', title='Fuhrpark', cars=cars)

@app.route('/track_state')
def track_state():
  track_state = TrackState.query.first()
  app.logger.info('got trackstate:' + repr(track_state))
  return render_template('track_state.html', title='Strecke', track_state=track_state, active_racers=[0,1,6])

@app.route('/refresh_track_state')
def refresh_track_state():
    track_state = TrackState.query.first()
    return jsonify(
      {
        'fuel_array': track_state.fuel_array(),
        'pit_array': track_state.pit_array(),
        'start_light': track_state.start_light,
      }
    )

@app.route('/car_registration', methods=['GET', 'POST'])
def register():
    form = CarRegistrationForm()
    if form.validate_on_submit():
        car = Car(ame=form.name.data, description=form.description.data, order_number=form.order_number.data, image_link=form.image_link.data)
        db.session.add(car)
        db.session.commit()
        flash('Ein neues Auto wurde dem Fuhrpark hinzugefügt')
        return redirect(url_for('index'))
    return render_template('car_registration.html', title='Neues Auto registrieren', form=form)
