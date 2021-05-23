from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextField, SubmitField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Optional
from wtforms.fields.html5 import DateField
from app.models import Racer, Car


class GridEntryForm(FlaskForm):
    class Meta:
        csrf = False
    controller = SelectField('Controller', choices=[(0, 1), (1, 2), (2, 3), (3, 4), (6, _l('Ghost'))])
    racer = SelectField(_l('Racer'), coerce=int)
    car = SelectField(_l('Car'), coerce=int)


class RaceRegistrationForm(FlaskForm):
    type = SelectField(
        'Art',
        choices=[('0', _l('Free roam')), ('1', _l('Training')), ('2', _l('Qualifying')), ('3', _l('Race')), ('4', _l('Time trial'))]
    )
    duration = SelectField(
        'Dauer',
        choices=[
            ('0', _l('unlimited')),
            ('1m', _l('1 Minute')),
            ('5m', _l('5 Minutes')),
            ('10m', _l('10 Minutes')),
            ('20m', _l('20 Minutes')),
            ('100l', _l('100 Laps')),
            ('500l', _l('500 Laps'))
        ]
    )
    status = HiddenField("created")
    grid = FieldList(FormField(GridEntryForm), min_entries=1)
    submit = SubmitField(_l('Start Race'))


class RacerRegistrationForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    submit = SubmitField(_l('Register Racer'))

    def validate_name(self, name):
        racer = Racer.query.filter_by(name=name.data).first()
        if racer is not None:
            raise ValidationError(_l('Racer already registered.'))


class CarRegistrationForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    description = TextField(_l('description'), validators=[DataRequired()])
    order_number = StringField(_l('Order No.'))
    image_link = StringField(_l('Image URL'))
    submit = SubmitField(_l('Add to Car Park'))

    def validate_order_number(self, order_number):
        car = Car.query.filter_by(order_number=order_number.data).first()
        if car is not None:
            raise ValidationError(_l('Car already registered'))


class SeasonForm(FlaskForm):
    description = TextField(_l('description'), validators=[DataRequired()])
    started_at = DateField(_l('season_from'), format='%Y-%m-%d')
    ended_at = DateField(_l('season_to'), format='%Y-%m-%d', validators=(Optional(),))
    submit = SubmitField(_l('Save Season'))
