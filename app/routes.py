import datetime
import json

from flask import request, render_template, flash, redirect, url_for
from flask_babel import lazy_gettext as _l
from app import app, db, services
from app.forms import CarRegistrationForm, RaceRegistrationForm, RacerRegistrationForm
from app.models import Car, Race, Racer


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/cars')
def cars():
    cars = Car.query.all()
    app.logger.info('got cars:' + repr(cars))
    return render_template('cars.html', title='Fuhrpark', cars=cars)


@app.route('/racers')
def racers():
    racers = Racer.query.all()
    app.logger.info('got racers:' + repr(racers))
    return render_template('racers.html', title='Fahrer', racers=racers)


@app.route('/races')
def races():
    races = Race.query.all()
    app.logger.info('got races:' + repr(races))
    return render_template('races.html', title='Erstellte Rennen', races=races)


@app.route('/races/<int:race_id>/stop')
def race_stop(race_id):
    race = Race.query.get(race_id)
    if race is not None:
        race.stop()
        db.session.add(race)
        db.session.commit()
        services.disconnect_control_unit()
        app.logger.info('stopping race:' + repr(race))
        flash(_l('Race stopped'))
    return render_template('races.html', title='Erstellte Rennen', races=Race.query.all())


@app.route('/demo')
def demo():
    services.mock_control_unit_connection()
    return render_template('current_race.html', title='Aktuelles Rennen', current_race=Race.current())


@app.route('/current_race')
def current_race():
    services.try_control_unit_connection()
    return render_template('current_race.html', title='Aktuelles Rennen', current_race=Race.current())


@app.route('/racer_registration', methods=['GET', 'POST'])
def racer_registration():
    form = RacerRegistrationForm()

    if form.validate_on_submit():
        racer = Racer(name=form.name.data)
        db.session.add(racer)
        db.session.commit()
        flash(_l('New racer registered'))
        return redirect(url_for('racers'))
    return render_template('racer_registration.html', title='Fahrer registrieren', form=form)


@app.route('/race_registration', methods=['GET', 'POST'])
def race_registration():
    form = RaceRegistrationForm(status='created')
    form.grid[0].racer.choices = [(r.id, r.name) for r in Racer.query.all()]
    form.grid[0].car.choices = [(c.id, c.name) for c in Car.query.all()]
    if request.method == 'POST':
        cancel_current_race()
        race = Race(
            type=form.type.data,
            duration=form.duration.data,
            status=form.status.data,
            created_at=datetime.datetime.now(),
            grid=json.dumps(form.grid.data)
        )
        db.session.add(race)
        db.session.commit()
        flash(_l('New race registered.'))
        return redirect(url_for('current_race'))
    return render_template('race_registration.html', title='Rennen anlegen', form=form)


@app.route('/car_registration', methods=['GET', 'POST'])
def register():
    form = CarRegistrationForm()
    if form.validate_on_submit():
        car = Car(name=form.name.data, description=form.description.data, order_number=form.order_number.data, image_link=form.image_link.data)
        db.session.add(car)
        db.session.commit()
        flash(_l('New car added to car park'))
        return redirect(url_for('index'))
    return render_template('car_registration.html', title='Neues Auto registrieren', form=form)


def cancel_current_race():
    race = Race.current()
    if race is None:
        return
    race.cancel()
    db.session.add(race)
    db.session.commit()
