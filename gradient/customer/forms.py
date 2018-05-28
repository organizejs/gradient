from flask_wtf import FlaskForm
from flask_security.forms import ConfirmRegisterForm
from wtforms.validators import (
  InputRequired, Optional, EqualTo, NumberRange,
  Length,
)
from wtforms import (
  IntegerField, StringField, SelectField, PasswordField, 
  BooleanField,
)
from .models import MaritalStatus
from ..util import StateCodes

DEPENDENTS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '>9']


class RequiredIf(Optional):
  '''
  Make field required if
  field is equal to specified value
  '''

  def __init__(self, other_field_name, value, *args, **kwargs):
    self.other_field_name = other_field_name
    self.value = value
    super(RequiredIf, self).__init__(*args, **kwargs)


  def __call__(self, form, field):
    other_field = form._fields.get(self.other_field_name)
    if other_field is None:
        raise Exception('no field named "%s" in form' % self.other_field_name)
    if other_field.data == self.value:
        super(RequiredIf, self).__call__(form, field)


class SignatureForm(FlaskForm):
  signature = StringField('Signature', [InputRequired()])


class DetailsForm(FlaskForm):
  street     = StringField('Street Address', [InputRequired()])
  city       = StringField('City', [InputRequired()])
  state_code = SelectField('State', [
                             InputRequired(),
                             Length(message="State codes is invalid", max=2)
                           ],
                           choices=StateCodes)
  zip_code   = StringField('Zip Code', [
                             InputRequired(),
                             Length(message="Zip code is invalid", min=5, max=12)
                           ])


class IncomeForm(FlaskForm):
  marital_status    = SelectField('Marital Status', 
                                  [InputRequired()],
                                  choices=MaritalStatus.choices(),
                                  coerce=MaritalStatus.coerce)
  dependents        = SelectField('Dependents', 
                                  [InputRequired()],
                                  choices=list(enumerate(DEPENDENTS)),
                                  coerce=int)
  individual_income = IntegerField('Individual Income', [
                                     RequiredIf('marital_status', MaritalStatus.MARRIED),
                                     NumberRange(min=0)
                                   ])
  household_income  = IntegerField('Household Income', [
                                     RequiredIf('marital_status', MaritalStatus.NOT_MARRIED),
                                     NumberRange(min=0)
                                   ])
  

class GradientSetupForm(IncomeForm, SignatureForm, DetailsForm):
  subscribe = BooleanField('Subscribe to the Gradient newsletter', [])


class GradientConfirmRegisterForm(ConfirmRegisterForm):
  first_name       = StringField('First Name', [InputRequired()])
  last_name        = StringField('Last Name', [InputRequired()])
  password_confirm = PasswordField('Confirm Password', [
                                     EqualTo('password', 
                                     message='Passwords must match')
                                   ])
  
