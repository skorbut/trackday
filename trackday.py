from app import app, db
from db import seeds
from app.models import Racer, Car, Lap

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Racer': Racer, 'Car': Car, 'Lap': Lap}