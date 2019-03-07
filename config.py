import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'my precioussss'
  #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_DATABASE_URI = "postgresql://trackday:trackday@localhost:5432/trackday"
  SQLALCHEMY_TRACK_MODIFICATIONS = False