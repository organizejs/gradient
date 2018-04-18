from functools import wraps
from flask import (
    Blueprint, abort, redirect, render_template, request, 
    jsonify, flash, url_for,
)
from flask_security import current_user
from flask_security.registerable import register_user
from flask_security.decorators import anonymous_user_required
from flask_security.forms import LoginForm
from .forms import (
  VendorConfirmRegisterForm, VendorRegisterForm, 
  DetailsForm, StripeKeysForm, RedirectUrlForm,
)
from .models import Vendor
from ..datastore import db
from ..transaction import Transaction
from ..user import Address

bp = Blueprint('vendor', __name__, url_prefix='/v')


def vendor_required(f):
  '''
  Decorator to require that account is authenticated and
  that account type is 'vendor'
  '''
  @wraps(f)
  def decorated(*args, **kwargs):
    if current_user.is_authenticated \
        and current_user.account_type == 'vendor':
      return f(*args, **kwargs)
    else:
      return redirect(url_for('customer.index'))
    abort(400)
  return decorated


@bp.route('/')
def index():
  '''
  If vendor is authenticated, redirect to home page
  If vendor is not authenticated, redirect to register
  '''
  if current_user.is_authenticated \
      and current_user.account_type == 'vendor':
    return redirect(url_for('vendor.home'))
  else:
    return redirect(url_for('vendor.register')) 


@bp.route('/login')
@anonymous_user_required
def login():
  '''
  Login page for vendor
  '''
  # TODO - eventually vendor login page should look different
  form = LoginForm()
  return render_template(
          'security/login_user.html',
          login_user_form=form)


@bp.route('/register', methods=['GET', 'POST'])
@anonymous_user_required
def register():
  '''
  Vendor registration page
  if GET - render the registration page
  if POST - validate the form and redirect to the 
      customer setup pages
  '''
  form = VendorRegisterForm()

  # if POST
  if request.method == 'POST' and form.validate_on_submit():
    registration_data = form.to_dict()
    data = form.data

    # create address model out of form
    address = Address()
    form.populate_obj(address)

    # create user model out of form, and add address
    user = register_user(**registration_data)
    user.address = address
    user.update_subscribe(data.get('subscribe'))

    # create vendor model out of user
    vendor = Vendor(user=user, 
                    company_name=data.get('company_name'))
    form.populate_obj(vendor)

    # commmit!
    db.session.add(vendor)
    db.session.commit()
    return redirect('/')

  # if GET
  return render_template('account/vendor/register.html', form=form)


@bp.route('/home')
@vendor_required
def home():
  '''
  Render vendor home page
  '''
  return redirect(url_for('vendor.purchases'))


@bp.route('/home/purchases')
@vendor_required
def purchases():
  '''
  Render purchases in home page
  '''
  return render_template('account/vendor/home.html')


@bp.route('/home/settings')
@vendor_required
def settings():
  '''
  Render settings in home page
  '''
  stripe_keys_form = StripeKeysForm()
  redirect_url_form = RedirectUrlForm()
  return render_template(
          'account/vendor/home.html',
          stripe_keys_form=stripe_keys_form,
          redirect_url_form=redirect_url_form)


@bp.route('/home/settings/stripe_keys', methods=['POST'])
@vendor_required
def stripe_keys():
  '''
  Vendor stripe keys submit
  '''
  form = StripeKeysForm()

  if form.validate_on_submit():
    data = form.data
    vendor = current_user.account
    vendor.stripe_sk = data.get('stripe_sk')
    vendor.stripe_pk = data.get('stripe_pk')
    db.session.commit()

    flash('You have successfully added your stripe keys.')
    return redirect(url_for('vendor.settings'))

  return jsonify(success=False, errors=form.errors)


@bp.route('/home/settings/stripe_keys/reset')
@vendor_required
def reset_stripe_keys():
  '''
  Reset vendor stripe keys
  '''
  vendor = current_user.account
  vendor.stripe_sk = None
  vendor.stripe_pk = None
  db.session.commit()
  flash('You have successfully removed your stripe keys.')
  return redirect(url_for('vendor.settings'))


@bp.route('/home/settings/redirect_url', methods=['POST'])
@vendor_required
def redirect_url():
  '''
  Vendor stripe keys submit
  '''
  form = RedirectUrlForm()

  if form.validate_on_submit():
    data = form.data
    vendor = current_user.account
    vendor.redirect_url = data.get('redirect_url')
    db.session.commit()

    flash('You have successfully added your redirect url.')
    return redirect(url_for('vendor.settings'))

  return jsonify(success=False, errors=form.errors)


@bp.route('/home/settings/redirect_url/reset')
@vendor_required
def reset_redirect_url():
  '''
  Reset vendor redirect url
  '''
  vendor = current_user.account
  vendor.redirect_url = None
  db.session.commit()
  flash('You have successfully removed your redirect url.')
  return redirect(url_for('vendor.settings'))


@bp.route('/register/validate/user', methods=['POST'])
def validate_user():
  '''
  Validation for vendor registration
  Validate user
  '''
  form = VendorConfirmRegisterForm(csrf_enabled=False)
  if form.validate_on_submit():
    return jsonify(success=True)
  else:
    return jsonify(success=False, errors=form.errors)


@bp.route('/register/validate/details', methods=['POST'])
def validate_details():
  '''
  Validation for vendor details
  Validate details form
  '''
  form = DetailsForm(csrf_enabled=False)
  if form.validate_on_submit():
    return jsonify(success=True)
  else:
    return jsonify(success=False, errors=form.errors)


