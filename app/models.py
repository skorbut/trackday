from app import db

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
  car_id = db.Column(db.Integer, db.ForeignKey('car.id'))

  time = db.Column(db.Integer, index=False, unique=False)

  def __repr__(self):
    return '<Lap {}>'.format(self.car_id)

class TrackState(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime)
  fuel_levels = db.Column(db.String(8)) # Eight-item list of fuel levels (0..15)
  cars_in_pit = db.Column(db.String(8)) # 8-bit pit lane bit mask
  start_light = db.Column(db.Integer)
  cars_to_display = db.Column(db.Integer)
  mode = db.Column(db.Integer)
  processed = db.Column(db.Boolean)

  def __repr__(self):
    return '<TrackEvent timestamp = {}, fuel_levels = {}, cars_in_pit = {}, start_light = {}>'.format(self.timestamp, self.fuel_levels, self.cars_in_pit, self.start_light)

  def fuel_array(self):
    return list(map(lambda x : int(x,16), list(self.fuel_levels)))
  def pit_array(self):
    return list(map(lambda x : bool(int(x)), list(self.cars_in_pit)))

