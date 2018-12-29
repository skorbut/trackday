from app import db

class Racer(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), index=True, unique=True)

  def __repr__(self):
    return '<Racer {}>'.format(self.name)

class Car(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), index=False, unique=False)
  token = db.Column(db.String(64), index=True, unique=True)

  def __repr__(self):
    return '<Car {}>'.format(self.name)

class Lap(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  car_id = db.Column(db.Integer, db.ForeignKey('car.id'))

  time = db.Column(db.Integer, index=False, unique=False)
