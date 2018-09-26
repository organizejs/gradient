import requests
import json
from functools import wraps
from flask import (
    Blueprint, abort, redirect, render_template, request, 
    jsonify, flash, url_for, current_app
)
from flask_security import current_user
from flask_security.registerable import register_user
from flask_security.decorators import anonymous_user_required
from flask_security.forms import LoginForm
from sqlalchemy import and_
from .forms import (
  VendorConfirmRegisterForm, VendorRegisterForm, 
  DetailsForm, RedirectUrlForm, ProductForm,
)
from .models import Vendor
from ..datastore import db
from ..transaction import Transaction
from ..user import Address
from ..product import Product
from ..stripe import stripe

bp = Blueprint('vendor', __name__, url_prefix='/v')


def vendor_required(f):
  '''
  Decorator to require that the account is authenticated and
  that account type is 'vendor'
  '''
  @wraps(f)
  def decorated(*args, **kwargs):
    if current_user.is_authenticated:
      if current_user.account_type == 'vendor':
        return f(*args, **kwargs)
      else:
        flash('You need to be logged into a vendor account to access those pages.')
        return redirect(url_for('main.index'))
    else:
      return current_app.login_manager.unauthorized()
    abort(400)
  return decorated


@bp.route('/')
def index():
  '''
  If vendor is authenticated, redirect to account page
  If vendor is not authenticated, redirect to register
  '''
  if current_user.is_authenticated \
      and current_user.account_type == 'vendor':
    return redirect(url_for('vendor.account'))
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


@bp.route('/account')
@vendor_required
def account():
  '''
  Render vendor account page
  '''
  return redirect(url_for('vendor.purchases'))


@bp.route('/account/purchases')
@vendor_required
def purchases():
  '''
  Render purchases in account page
  '''
  return render_template('vendor/account/purchases.html')


@bp.route('/account/settings')
@vendor_required
def settings():
  '''
  Render settings in account page
  '''
  redirect_url_form = RedirectUrlForm()
  stripe_connect_account_link = "https://connect.stripe.com/oauth/authorize?response_type=code&client_id={}&scope=read_write".format(stripe.connect_client_id)

  return render_template(
           'vendor/account/settings.html',
           stripe_connect_account_link=stripe_connect_account_link,
           redirect_url_form=redirect_url_form)


@bp.route('/account/product/<int:product_id>')
@vendor_required
def product(product_id):
  '''
  Render product page in account page for specified product
  '''
  product = Product.query.filter_by(id=product_id).first()
  return render_template(
           'vendor/account/product.html',
           product=product)


@bp.route('/account/products')
@vendor_required
def products():
  '''
  Render products page in account page
  '''
  products = Product.query \
    .filter_by(vendor=current_user.account, active=True).all()
  return render_template(
           'vendor/account/products.html',
           products=products)


@bp.route('/account/add_product_form')
@vendor_required
def add_product_form():
  '''
  Render add product form in accountpage
  '''
  product_form = ProductForm()
  return render_template(
           'vendor/account/add_product_form.html',
           product_form=product_form)


@bp.route('/account/edit_product_form/<int:product_id>')
@vendor_required
def edit_product_form(product_id):
  '''
  Render edit product form in account page
  '''
  product = Product.query.filter_by(id=product_id).first()
  product_form = ProductForm(
    product_sku=product.sku,
    product_name=product.name,
    image_url=product.image_url,
    max_price=product.max_price,
    min_price=product.min_price)

  return render_template(
           'vendor/account/edit_product_form.html',
           product=product,
           product_form=product_form)


@bp.route('/account/stripe', methods=['GET'])
@vendor_required
def stripe_authentication():
  scope = request.args.get('scope')
  code = request.args.get('code')
  error = request.args.get('error')
  error_desc = request.args.get('error_description')
  if error is None:
    # fetch user's credentials from Stripe
    stripe_url = "https://connect.stripe.com/oauth/token"
    resp = requests.post(stripe_url, params={
      "client_secret": stripe.secret_key,
      "code": code, 
      "grant_type": "authorization_code"
    })
    if resp.ok:
      # deserialize response content 
      response_content = resp.content.decode("utf-8")
      response_json = json.loads(response_content)

      # update database
      vendor = current_user.account
      vendor.stripe_is_authorized = True
      vendor.stripe_account_resp = response_content
      vendor.stripe_publishable_key = response_json['stripe_publishable_key']
      vendor.stripe_user_id = response_json['stripe_user_id']
      vendor.stripe_refresh_token = response_json['refresh_token']
      vendor.stripe_access_token = response_json['access_token']
      db.session.commit()

      flash('Success! Your Stripe account has been added.')
      return redirect(url_for('vendor.settings'))

    else:
      flash('Could not create Stripe account: {}'.format(error_desc))
      return redirect(url_for('vendor.settings'))

  else:
    flash('Could not create Stripe account: {}'.format(error_desc))
    return redirect(url_for('vendor.settings'))


@bp.route('/account/settings/redirect_url', methods=['POST'])
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


@bp.route('/account/settings/redirect_url/reset')
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


@bp.route('/account/edit_product_form/delete_product/<int:product_id>', methods=['POST'])
@vendor_required
def delete_product(product_id):
  '''
  Delete the specified product
  1. Check that product exists
  2. Delete product from db
  '''
  product = Product.query.filter_by(id=product_id).first()
  if product is not None:

    # set to inactive
    product.active = False
    db.session.commit()

    flash('You have deleted the product: %s' % product.name)
    return redirect(url_for('vendor.products'))
  else:
    flash("ERROR product id DNE")
    return redirect(url_for('vendor.products'))


@bp.route('/account/edit_product_form/edit_product/<int:product_id>', methods=['POST'])
@vendor_required
def edit_product(product_id):
  '''
  Edit product associated to the vendor
  '''
  form = ProductForm()

  if form.validate_on_submit():
    data = form.data
    vendor = current_user.account

    product = Product.query.filter_by(id=product_id).first()
    product.sku = data.get('product_sku')
    product.name = data.get('product_name')
    product.max_price = data.get('max_price')
    product.min_price = data.get('min_price')
    product.image_url = data.get('image_url')

    db.session.add(product)
    db.session.commit()

    flash('Your product has been updated')
    return redirect(url_for('vendor.products'))
  
  return jsonify(success=False, errors=form.errors)


@bp.route('/account/add_product_form/add_product', methods=['POST'])
@vendor_required
def add_product():
  '''
  Add a product associated to the vendor
  '''
  form = ProductForm()

  if form.validate_on_submit():
    data = form.data
    vendor = current_user.account

    product = Product(vendor=vendor,
                      sku=data.get('product_sku'),
                      name=data.get('product_name'),
                      max_price=data.get('max_price'),
                      min_price=data.get('min_price'),
                      image_url=data.get('image_url'))

    db.session.add(product)
    db.session.commit()

    flash('Your product(s) have been added')
    return redirect(url_for('vendor.products'))
  
  return jsonify(success=False, errors=form.errors)
   

# ======================
# ==== Registration ====
# ======================

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

    # register_user() - sends confirmation email and encrypts password
    user = register_user(**registration_data) 
    user.address = address
    user.update_subscription(data.get('subscribe'))
    db.session.add(user)

    # create vendor model out of user
    vendor = Vendor(user=user, company_name=data.get('company_name'))
    form.populate_obj(vendor)

    # commmit!
    db.session.add(vendor)
    db.session.commit()
    return redirect('/')

  # if GET
  return render_template('vendor/register.html', form=form)


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


