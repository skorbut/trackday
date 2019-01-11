from app import app, db
from db import seeds
from app.models import Car, Lap, Race, Racer

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Car': Car, 'Lap': Lap, 'Race': Race, 'Racer': Racer}