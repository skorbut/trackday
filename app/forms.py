from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import ValidationError, DataRequired

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