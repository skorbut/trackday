import logging, os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
socketio = SocketIO(app, logger=True, engineio_logger=True)

if __name__ == '__main__':
    socketio.run(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/trackday.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

app.logger.info('Trackday App started successfully')


from app import routes, models, errors, services
# to re init database use this import
#from app import models