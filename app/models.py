import datetime
import json
from sqlalchemy import inspect, func, or_
from app import app, db


class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16))
    duration = db.Column(db.Integer)
    grid = db.Column(db.String(128))
    status = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)

    def parsed_grid(self):
        if self.grid is None:
            return None
        return list(
            map(
                lambda grid_entry: {
                    'controller': grid_entry['controller'],
                    'racer': Racer.query.get(grid_entry['racer']),
                    'car': Car.query.get(grid_entry['car'])
                },
                json.loads(self.grid)
            )
        )

    def cancel(self):
        self.status = "cancelled"
        self.finished_at = datetime.datetime.now()

    def start(self):
        app.logger.info("setting race status to started and adding started_at timestamp")
        self.status = "started"
        self.started_at = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def stop(self):
        app.logger.info("stopping race and adding finished_at timestamp")
        self.status = "stopped"
        self.finished_at = datetime.datetime.now()

    def add_lap(self, controller, time):
        lap = Lap(
            race_id=self.id,
            controller=controller,
            time=time,
            racer_id=self.racer(controller).id,
            car_id=self.car(controller).id
        )
        db.session.add(lap)
        db.session.commit()
        return lap

    def racer(self, controller):
        for grid_entry in self.parsed_grid():
            if(grid_entry['controller'] == str(controller)):
                return grid_entry['racer']
        app.logger.info("Unable to find racer for controller " + repr(controller) + " in grid " + repr(self.parsed_grid()))
        return None

    def car(self, controller):
        for grid_entry in self.parsed_grid():
            if(grid_entry['controller'] == str(controller)):
                return grid_entry['car']
        app.logger.info("Unable to find car for controller " + repr(controller) + " in grid " + repr(self.parsed_grid()))
        return None

    def controller_for_racer(self, racer):
        for grid_entry in self.parsed_grid():
            if(grid_entry['racer'] == racer):
                return grid_entry['controller']
        return None

    def lap_count_by_racer(self, racer):
        return self.lap_count_by_controller(racer)

    def lap_count_by_racers(self):
        lap_counts = {}
        for grid_entry in self.parsed_grid():
            lap_counts[grid_entry['racer']] = self.lap_count_by_controller(grid_entry['controller'])
        return lap_counts

    def lap_count_by_controller(self, controller):
        if controller is None:
            return 0
        return self.statistics().lap_count_by_controller(controller)

    def laps_by_controller(self, controller):
        if controller is None:
            return 0
        return Lap.query.filter_by(race_id=self.id, controller=controller)

    def denormalize_laps(self):
        for l in Lap.query.filter_by(race_id=self.id).all():
            for grid_entry in self.parsed_grid():
                if(int(grid_entry['controller']) == l.controller):
                    l.racer_id = grid_entry['racer'].id
                    l.car_id = grid_entry['car'].id
                    db.session.commit()

    def statistics(self):
        return Statistics(self)

    @staticmethod
    def current():
        return next(iter(Race.query.filter(or_(Race.status == 'created', Race.status == 'started')).all()), None)


class Racer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Racer {}>'.format(self.name)

    def fastest_laps(self):
        return Lap.query.filter(Lap.time > 1000, Lap.racer_id == self.id).order_by(Lap.time).limit(5).all()


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=False, unique=False)
    description = db.Column(db.String(512), index=False, unique=False)
    order_number = db.Column(db.String(16), index=True, unique=True)
    image_link = db.Column(db.String(128), index=False, unique=False)

    def __repr__(self):
        return '<Car {}>'.format(self.name)

    def fastest_laps(self):
        return Lap.query.filter(Lap.time > 1000, Lap.car_id == self.id).order_by(Lap.time).limit(5).all()


class Lap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'))
    racer_id = db.Column(db.Integer, db.ForeignKey('racer.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    controller = db.Column(db.Integer)
    time = db.Column(db.Integer, index=False, unique=False)

    def __repr__(self):
        return '<Lap {} {}>'.format(self.controller, self.time)

    def to_json(self):
        return json.dumps({c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs})

    def racer(self):
        return Racer.query.get(self.racer_id)

    def car(self):
        return Car.query.get(self.car_id)

    def formatted_time(self):
        return '{:05.3f} s'.format(self.time / 1000)


class Timing(object):
    def __init__(self, num):
        self.num = num
        self.time = None
        self.lap_time = None
        self.best_time = None
        self.laps = 0

    def newlap(self, timer):
        if self.time is not None:
            self.lap_time = timer.timestamp - self.time
        if self.best_time is None or self.lap_time < self.best_time:
            self.best_time = self.lap_time
        self.laps += 1
        self.time = timer.timestamp


class Statistics:
    def __init__(self, race):
        self.race = race

    def race_time_by_controller(self, controller):
        time = self.function_on_laps_by_controller(controller, func.sum(Lap.time).label('race_time'))
        return self.format_duration(time)

    def lap_count_by_controller(self, controller):
        if controller is None:
            return 0
        return Lap.query.filter_by(race_id=self.race.id, controller=controller).count()

    def fastest_lap_by_controller(self, controller):
        time = self.function_on_laps_by_controller(controller, func.min(Lap.time).label('minimum_lap_time'))
        return self.format_duration(time)

    def slowest_lap_by_controller(self, controller):
        time = self.function_on_laps_by_controller(controller, func.max(Lap.time).label('maximum_lap_time'))
        return self.format_duration(time)

    def average_lap_by_controller(self, controller):
        time = self.function_on_laps_by_controller(controller, func.avg(Lap.time).label('average_lap_time'))
        return self.format_duration(time)

    def function_on_laps_by_controller(self, controller, function):
        if controller is None:
            return None
        calculated = Lap.query.with_entities(function).filter(
            Lap.time > 1000,
            Lap.controller == controller,
            Lap.race_id == self.race.id
        ).one()[0]
        if calculated is None:
            return None
        try:
            return datetime.timedelta(milliseconds=calculated)
        except TypeError:
            return None

    def format_duration(self, duration):
        if duration is None:
            return None
        total_seconds = duration.total_seconds()
        hours, remainder = divmod(total_seconds, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return '{:02d}:{:02d}:{:05.3f} hours'.format(int(hours), int(minutes), seconds)
        if minutes > 0:
            return '{:02d}:{:05.3f} min'.format(int(minutes), seconds)

        return '{:05.3f} s'.format(seconds)
