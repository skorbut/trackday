from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import ValidationError, DataRequired
from app import db
from app.models import Race, Racer, Car

class GridEntryForm(FlaskForm):
  class Meta:
    csrf = False
  controller = SelectField('Controller', choices=[(0,1), (1,2), (2,3), (3,4), (6, 'Ghost')])
  racer = SelectField('Fahrer', coerce=int)
  car =  SelectField('Auto', coerce=int)

class RaceRegistrationForm(FlaskForm):
  type = SelectField('Art', choices=[('0', 'Freie Fahrt'), ('1', 'Training'), ('2', 'Qualifikation'), ('3', 'Rennen')])
  duration = SelectField('Dauer', choices=[('0', 'unbegrenzt'), ('5', '5 Minuten'), ('10', '10 Minuten'), ('20', '20 Minuten')])
  status = HiddenField("created")
  grid = FieldList(FormField(GridEntryForm), min_entries=1)
  submit = SubmitField('Rennen starten')

class RacerRegistrationForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  submit = SubmitField('Fahrer registrieren')

  def validate_name(self, name):
    racer = Racer.query.filter_by(name=name.data).first()
    if racer is not None:
      raise ValidationError('Fahrer mit diesem Namen ist schon registriert.')

class CarRegistrationForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  description = TextField('Beschreibung', validators=[DataRequired()])
  order_number = StringField('Bestellnummer')
  image_link = StringField('Bildlink')
  submit = SubmitField('In Fuhrpark aufnehmen')

  def validate_order_number(self, order_number):
    car = Car.query.filter_by(order_number=order_number.data).first()
    if car is not None:
      raise ValidationError('Auto mit dieser Nummer ist schon registriert.')