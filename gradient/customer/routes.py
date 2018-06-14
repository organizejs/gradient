import stripe
from functools import wraps
from flask import (
  Blueprint, jsonify, redirect, render_template, 
  abort, url_for, flash, request, session
)
from flask_security import current_user, login_user
from flask_security.registerable import register_user
from flask_security.decorators import anonymous_user_required
from stripe.error import CardError, InvalidRequestError
from .forms import (
  SignatureForm, 
  IncomeForm, 
  GradientConfirmRegisterForm, 
  GradientSetupForm,
  DetailsForm,
)
from .models import Customer
from ..datastore import db
from ..user import Address

bp = Blueprint('customer', __name__, url_prefix='/c')


def customer_required(f):
  '''
  Decorator to require that account is authenticated and
  that account type is 'customer'
  '''
  @wraps(f)
  def decorated(*args, **kwargs):
    if current_user.is_authenticated \
        and current_user.account_type == 'customer':
      return f(*args, **kwargs)
    else:
      return redirect(url_for('customer.index'))
    abort(400)
  return decorated


@bp.route('/')
def index():
  '''
  If customer is authenticated, redirect to account page
  If customer is not authenticated, redirect to register
  '''
  if current_user.is_authenticated \
      and current_user.account_type == 'customer':
    return redirect(url_for('customer.account'))
  else:
    return redirect(url_for('customer.register'))


@bp.route('/account')
@customer_required
def account():
  '''
  Render customer account page
  '''
  return redirect(url_for('customer.purchases'))


@bp.route('/account/purchases')
@customer_required
def purchases():
  '''
  Render purchases in account page
  '''
  return render_template('account/customer/account.html')


@bp.route('/account/income')
@customer_required
def income():
  '''
  Render income in account page
  '''
  return render_template('account/customer/account.html')


@bp.route('/account/settings')
@customer_required
def settings():
  '''
  Render settings in account page
  '''
  return render_template('account/customer/account.html')


@bp.route('/account/settings/subscribe/<subscribe>')
@customer_required
def subscribe(subscribe):
  '''
  Subscribe Customer
  '''
  if subscribe:
    current_user.update_subscription(True);
    flash('Thank you for subscribing.')
  else:
    current_user.update_subscription(False);
    flash('You have successfully unsubscribed.')

  db.session.commit()
  return redirect(url_for('customer.settings'))


@bp.route('/account/settings/add_card', methods=['POST'])
@customer_required
def add_card():
  '''
  add a card to the customer
  if stripe_customer dne for customer, create one
  '''
  data = request.form
  stripe_token = data['token']

  customer = current_user.account

  try:
    if customer.stripe_id is None:
      stripe_customer = stripe.Customer.create(
        email=customer.user.email,
        source=stripe_token
      )
      customer.stripe_id = stripe_customer.id
      db.session.add(customer)
      db.session.commit()
    else:
      stripe_customer = stripe.Customer.retrieve(customer.stripe_id)

    card = stripe_customer.sources.create(source=stripe_token)
    session['new_card_id'] = card.id
    flash('Your card has been added')
    return redirect(request.referrer or url_for('customer.settings'))

  except (CardError, InvalidRequestError) as e:
    print("Exception: called 'add card'")
    return jsonify(success=False, error=e._message), 400


# ===================================
# ==== Registration & Onboarding ====
# ===================================

@bp.route('/register', methods=['GET', 'POST'])
@anonymous_user_required
def register():
  '''
  Customer registration page
  if GET - render the registration page
  if POST - validate the form and redirect to the 
      customer setup pages
  '''
  form = GradientConfirmRegisterForm()

  # if POST
  if form.validate_on_submit():
    data = form.to_dict()

    # register_user() - sends confirmation email and encrypts password
    user = register_user(**data)

    customer = Customer(user=user)
    form.populate_obj(customer)
    db.session.add(customer)
    db.session.commit()

    login_user(user)
    return redirect(url_for('customer.onboarding'))

  # if GET 
  return render_template(
    'account/customer/register.html',
    register_user_form=form)


@bp.route('/register/validate/signature', methods=['POST'])
def validate_signature():
  # TODO reroute to /onboarding
  '''
  Validation for onboarding flow
  Validate signature form
  '''
  form = SignatureForm(csrf_enabled=False)
  if form.validate_on_submit():
    return jsonify(success=True)
  return jsonify(success=False, errors=form.errors)


@bp.route('/register/validate/income', methods=['POST'])
def validate_income():
  # TODO reroute to /onboarding
  '''
  Validation for onboarding flow
  Validate income form
  '''
  form = IncomeForm(csrf_enabled=False)
  if form.validate_on_submit():
    return jsonify(success=True)
  return jsonify(success=False, errors=form.errors)


@bp.route('/register/validate/details', methods=['POST'])
def validate_details():
  # TODO reroute to /onboarding
  '''
  Validation for customer details
  Validate details form
  '''
  form = DetailsForm(csrf_enabled=False)
  if form.validate_on_submit():
    return jsonify(success=True)
  else:
    return jsonify(success=False, errors=form.errors)


@bp.route('/onboarding', methods=['GET', 'POST'])
@customer_required
def onboarding():
  '''
  Customer onboarding pages
  if GET - render the onboarding pages
  if POST - validate the form and redirect to the 
      index page
  '''
  form = GradientSetupForm()

  # if POST
  if form.validate_on_submit():
    data = form.data

    # get address for user if exists otherwise create one
    address = None
    if not current_user.address:
      address = Address()
    else:
      address = Address.query.filter_by(id=current_user.address.id).first() #?

    # populate address model from form
    form.populate_obj(address)
    current_user.address = address
    current_user.update_subscription(data.get('subscribe'));

    # get and populate customer 
    customer = current_user.account
    form.populate_obj(customer)

    # commit!
    db.session.add(customer)
    db.session.commit()

    flash('Thank you. Your account setup is complete.')
    return redirect('/')

  # if GET
  return render_template('account/customer/onboarding.html', form=form)

