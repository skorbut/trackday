import datetime, json
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
    #parse to json
    #replace racer and car with objects
    return list(map(lambda grid_entry: {'controller': grid_entry['controller'], 'racer': Racer.query.get(grid_entry['racer']), 'car': Car.query.get(grid_entry['car'])}, json.loads(self.grid)))

  def cancel(self):
    self.status = "cancelled"
    self.finished_at = datetime.datetime.now()
    db.add(self)
    db.commit()

  def start(self):
    self.status = "started_at"
    self.started_at = datetime.datetime.now()
    db.add(self)
    db.commit()

  @staticmethod
  def current():
    return next(iter(Race.query.filter(Race.status=='created').all()), None)

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


