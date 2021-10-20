import datetime
import json

from flask import request, render_template, flash, redirect, url_for
from flask_babel import lazy_gettext as _l
from app import app, db, race_handler
from app.forms import CarRegistrationForm, RaceRegistrationForm, RacerRegistrationForm, SeasonForm
from app.models import Car, Race, Racer, Season
from app.track_listener import start_track_listener, stop_track_listener, track_listener_running
from app.observers import LoggingDebugObserver


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/cars')
def cars():
    cars = Car.query.all()
    app.logger.info('got cars:' + repr(cars))
    return render_template('cars.html', title='Fuhrpark', cars=cars)


@app.route('/cars/<int:car_id>')
def car(car_id):
    car = Car.query.get(car_id)
    last_season = Season.query.filter(Season.ended_at.isnot(None)).order_by(Season.ended_at.desc()).first()
    return render_template('car.html', title='Auto', car=car, last_season=last_season, current_season=Season.current())


@app.route('/racers')
def racers():
    racers = Racer.query.all()
    last_season = Season.query.filter(Season.ended_at.isnot(None)).order_by(Season.ended_at.desc()).first()
    app.logger.info('got racers:' + repr(racers))
    return render_template('racers.html', title='Fahrer', racers=racers, last_season=last_season, current_season=Season.current())


@app.route('/races')
def races():
    races = Race.query.all()
    app.logger.info('got races:' + repr(races))
    return render_template('races.html', title='Erstellte Rennen', races=races)


@app.route('/races/<int:race_id>/stop')
def race_stop(race_id):
    race = Race.query.get(race_id)
    if race is not None:
        race_handler.finish(race)
        flash(_l('Race stopped'))
    return redirect(url_for('race_result', race_id=race.id))


@app.route('/races/<int:race_id>/delete')
def race_delete(race_id):
    race = Race.query.get(race_id)
    if race is not None:
        race.stop()
        db.session.delete(race)
        db.session.commit()
        app.logger.info('deleting race:' + repr(race))
        flash(_l('Race deleted'))
    return render_template('races.html', title='Erstellte Rennen', races=Race.query.all())


@app.route('/races/<int:race_id>/copy')
def race_copy(race_id):
    race = Race.query.get(race_id)
    if race is not None:
        new_race = Race(
            type=race.type,
            duration=race.duration,
            status='created',
            created_at=datetime.datetime.now(),
            grid=race.grid
        )
        db.session.add(new_race)
        db.session.commit()
        flash(_l('New race registered.'))
        race_handler.start(race)
        return redirect(url_for('current_race'))
    return render_template('races.html', title='Erstellte Rennen', races=Race.query.all())


@app.route('/races/<int:race_id>/result')
def race_result(race_id):
    race = Race.query.get(race_id)
    if race is not None:
        return render_template('race_result.html', title='Rennen beendet', race=race)
    return redirect(url_for('races'))


@app.route('/current_race')
def current_race():
    race = Race.current()
    if race is not None:
        if not race_handler.attach(race):
            flash(_l('No control unit connection!'))
    return render_template('current_race.html', title='Aktuelles Rennen', current_race=race)


@app.route('/quick_race')
def quick_race():
    if not race_handler.attach_quick_race():
        flash(_l('No control unit connection!'))
    return render_template('quick_race.html', title='Quick Race', current_season=Season.current())


@app.route('/races/<int:race_id>')
def race(race_id):
    return render_template('race.html', title='Rennen vom ', race=Race.query.get(race_id))


@app.route('/seasons')
def seasons():
    seasons = Season.query.all()
    app.logger.info('got seasons:' + repr(seasons))
    return render_template('seasons.html', title='Saison', seasons=seasons)


@app.route('/seasons/<int:season_id>')
def season(season_id):
    return render_template('season.html', title='Saison', season=Season.query.get(season_id))


@app.route('/seasons/new', methods=['GET', 'POST'])
def new_season():
    form = SeasonForm()

    if form.validate_on_submit():
        season = Season(
            description=form.description.data,
            started_at=form.started_at.data,
            ended_at=form.ended_at.data
        )
        db.session.add(season)
        db.session.commit()
        flash(_l('New season created'))
        return redirect(url_for('seasons'))
    return render_template('season_edit.html', title='Saison anlegen', form=form)


@app.route('/seasons/<int:season_id>/edit', methods=['GET', 'POST'])
def edit_season(season_id):
    season = Season.query.get(season_id)
    form = SeasonForm(obj=season)

    if form.validate_on_submit():
        form.populate_obj(season)
        db.session.add(season)
        db.session.commit()
        flash(_l('Season updated'))
        return redirect(url_for('seasons'))

    return render_template('season_edit.html', title='Saison bearbeiten', form=form, season=season)


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
        if race_handler.start(race):
            flash(_l('New race registered.'))
            return redirect(url_for('current_race'))
        else:
            flash(_l('Race not started. No control unit connection!'))
            return render_template('race.html', title='Rennen vom ', race=race)
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


@app.route('/track_listener')
def track_listener():
    return render_template('track_listener.html', title='Verbindung zur Strecke', track_listener_running=track_listener_running())


@app.route('/track_listener_start')
def track_listener_start():
    start_track_listener(LoggingDebugObserver(), LoggingDebugObserver())
    return redirect(url_for('track_listener'))


@app.route('/track_listener_stop')
def track_listener_stop():
    stop_track_listener()
    return redirect(url_for('track_listener'))


def cancel_current_race():
    race = Race.current()
    if race is None:
        return
    race_handler.finish(race)
