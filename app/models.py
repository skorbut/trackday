import datetime
import json
from sqlalchemy import inspect
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
    demo_mode = db.Column(db.Boolean, default=True)

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

    def stop(self):
        app.logger.info("stopping race and adding finished_at timestamp")
        self.status = "stopped"
        self.finished_at = datetime.datetime.now()

    def controller_for_racer(self, racer):
        for grid_entry in self.parsed_grid():
            if(grid_entry['Racer'] == racer):
                return grid_entry['Controller']
        return None

    def lap_count_by_racer(self, racer):
        return self.lap_count_by_controller(racer)

    def lap_count_by_controller(self, controller):
        if controller is None:
            return 0
        return Lap.query.filter_by(race_id=self.id, controller=controller).count()

    @staticmethod
    def current():
        return next(iter(Race.query.filter(Race.status == 'created').all()), None)


class Racer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Racer {}>'.format(self.name)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=False, unique=False)
    description = db.Column(db.String(512), index=False, unique=False)
    order_number = db.Column(db.String(16), index=True, unique=True)
    image_link = db.Column(db.String(128), index=False, unique=False)

    def __repr__(self):
        return '<Car {}>'.format(self.name)


class Lap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'))
    controller = db.Column(db.Integer)
    time = db.Column(db.Integer, index=False, unique=False)

    def __repr__(self):
        return '<Lap {} {}>'.format(self.controller, self.time)

    def to_json(self):
        return json.dumps({c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs})


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
