from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired, Optional, Email
from wtforms import BooleanField, StringField, RadioField, SelectField

class SubscribeForm(FlaskForm):
    email           = StringField('Email', [InputRequired(), Email()])
