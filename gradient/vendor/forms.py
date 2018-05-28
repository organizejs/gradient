from flask_wtf import FlaskForm
from wtforms.fields.html5 import IntegerField, DecimalField
from flask_security.forms import ConfirmRegisterForm
from wtforms.validators import (
  InputRequired, DataRequired, EqualTo, URL, NumberRange,
  Length,
)
from wtforms import (
  BooleanField, StringField, PasswordField, SubmitField,
  SelectField,
)
from ..util import StateCodes


class ProductForm(FlaskForm):
  product_sku   = StringField('Product SKU', [InputRequired()])
  product_name  = StringField('Product Name', [InputRequired()])
  image_url     = StringField('Product Thumbnail Url', [
                                InputRequired(), 
                                URL(message='This is not a valid URL')
                              ])
  max_price     = IntegerField('Maximum Price', [InputRequired()])
  min_price     = IntegerField('Maximum Price', [InputRequired()])


class StripeKeysForm(FlaskForm):
  stripe_sk = StringField('Stripe Secret Key', [InputRequired()])
  stripe_pk = StringField('Stripe Public Key', [InputRequired()])


class RedirectUrlForm(FlaskForm):
  redirect_url = StringField('Redirect URL', 
                             [URL(message='Sorry this is not a valid URL')])


class DetailsForm(FlaskForm):
  company_name = StringField('Company Name', [InputRequired()])
  street       = StringField('Street Address', [InputRequired()])
  city         = StringField('City', [InputRequired()])
  state_code   = SelectField('State', [
                               InputRequired(),
                               Length(message="State codes is invalid", max=2)
                             ],
                             choices=StateCodes)
  zip_code     = StringField('Zip Code', [InputRequired()])
  subscribe    = BooleanField('Subscribe for the Gradient newsletter', [])


class VendorConfirmRegisterForm(ConfirmRegisterForm):
  first_name       = StringField('First Name', [InputRequired()])
  last_name        = StringField('Last Name', [InputRequired()])
  password_confirm = PasswordField('Confirm Password', 
                                   [EqualTo('password', message='Passwords must match')])


class VendorRegisterForm(DetailsForm, VendorConfirmRegisterForm):
  pass
