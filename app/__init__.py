import logging
import os
from flask import Flask, request
from flask_babel import Babel
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
socketio = SocketIO(app, logger=True, engineio_logger=True)
babel = Babel(app)

if __name__ == '__main__':
    socketio.run(app)

if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler(
    'logs/trackday.log',
    maxBytes=10240,
    backupCount=10
)
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_ECHO'] = False

app.logger.info('Trackday App started successfully')


@babel.localeselector
def get_locale():
    app.logger.info("trying to get texts in language {}".format(request.accept_languages.best_match(app.config['LANGUAGES'])))
    return request.accept_languages.best_match(app.config['LANGUAGES'])


app.logger.info('Importing routes, models, errors and services')
from app import routes, models, errors
