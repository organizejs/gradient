import stripe
from stripe.error import CardError, InvalidRequestError
from flask_cors import cross_origin
from flask_security import login_required, current_user
from flask import (
  Blueprint, render_template, jsonify, request, redirect, 
  url_for, session, current_app, abort
)
from ..util import set_query_parameter
from ..product import Product
from ..vendor import Vendor
from ..customer.routes import customer_required
from ..transaction import Transaction
from ..datastore import db

bp = Blueprint('checkout', __name__, url_prefix='/checkout')


@bp.route('/initialize', methods=['POST'])
@cross_origin()
def initialize():
  '''
  This route starts the checkout flow.

  A vendor POSTs the following data to this endpoint
  to start the checkout flow (using gradient.js):

  {
    "vendor_id": "<vendor_id">,
    "products": [{
      sku: "<product_0_sku>",
      quantity: "<product_0_quantity>",
    }, ...]
  }

  1. create transaction object with transaction state OPEN
  2. use financial model to compute price for user
  3. create gradient_price object(s) with computed price
  4. render payment page with computed price
  '''
  # get vendor and products from POST body (json)
  checkout_content = request.get_json()
  vendor_id = checkout_content['vendor_id']
  vendor = Vendor.query.get_or_404(vendor_id)
  products = checkout_content['products']
  requester_url = request.environ['HTTP_REFERER']

  # create transaction object with OPEN transaction.status
  current_transaction = Transaction(
    vendor=vendor,
    requester_url=requester_url,
    status=Transaction.Status.OPEN)

  # create cart that is a mapping of sku:quantity
  # this will also remove any duplicates
  cart = {}
  for product in products:
    sku = product['sku']
    quantity = product['quantity']

    if sku not in cart:
      cart[sku] = int(quantity)
    else:
      cart[sku] = int(cart[sku]) + int(quantity)

  # add sku/quantity of each product in cart to the transaction
  for sku, quantity in cart.items():
    success = current_transaction.add_product(sku, quantity, vendor)
    if not success:
      abort(404)

  db.session.add(current_transaction)
  db.session.commit()

  return jsonify(success=True,
                 key=current_transaction.key,
                 url=url_for('checkout.cart', 
                             txid=current_transaction.uuid, 
                             _external=True))


@bp.route('/cart')
def cart():
  '''
  Displays the checkout page for a customer,
  listing the products they are about to pay for,
  with their respective Gradient prices. 
  
  But first we check if they are the owner of the 
  transaction and that the transaction is still OPEN.
  '''
  # get current transaction
  transaction_id = request.args.get('txid', -1)
  transaction = Transaction.query \
                           .filter_by(uuid=transaction_id) \
                           .first_or_404()

  # redirect the user if they are not authenticated
  if not current_user.is_authenticated:
    if '_tids' not in session:
      session['_tids'] = []
    session['_tids'].append(transaction_id)
    return current_app.login_manager.unauthorized()

  # block if user is not of type customer
  if current_user.account_type != 'customer':
    return 'Not a customer', 400

  # set ownership of transaction to current_user/customer
  if transaction.customer == None:
    # TODO: this has some security implications ideally we set
    #   ownership of this transaction via a session variable
    customer = current_user.account
    transaction.customer = customer

    valid, err = validate_transaction(transaction, customer)
    if not valid:
      return err['message'], err['code']

    db.session.add(transaction)
    db.session.commit()

  # TODO - get gradient price using "price()" and update transaction
  return render_template(
          'checkout.html',
          transaction=transaction,
          logged_in=True)


def validate_transaction(transaction, customer):
  '''
  Validates a transaction for a given user
  '''
  # check that transaction is OPEN
  if transaction.status != Transaction.Status.OPEN:
    return False, {'message': 'Transaction is not open', 'code': 403}

  # check that authenticated user is transaction owner
  if transaction.customer != customer:
    return False, {'message': 'Not owner of transaction', 'code': 401}

  return True, {}


def price(user, product):
  '''
  calculates unique gradient price and
  update transaction model with products

  returns GradientPrice

  TODO: implement real sliding scale
        for now just return mean of min and max
  '''
  # min_price = product.min_price * product.max_price
  # if user is None:
  #   return max_price
  # else:
  #   m = (max_price - min_price)/(vendor.min_income - vendor.max_income)
  #   return min_price + (m*(user.individual_income - vendor.max_income))
  return (product.max_price + product.min_price)/2


@bp.route('/pay', methods=['POST'])
@customer_required
def pay():
  '''
  Process payment for a transaction.
  expects the following POSTed form data:
    {
      'transaction_id': uuid,
      'token': str
    }
  validates:
    - user is authenticated
    - transaction exists
    - transaction has status of OPEN
    - authenticated user is transaction owner
  if payment is successful, transaction status is set to SUCCESS
  and the user is redirected to the vendor URL with params
  describing the transaction (the id and vendor).
  These params should be used by the vendor to validate the
  transaction was successfully completed (see gradient.js).
  '''

  data = request.form
  transaction_id = data['txid']
  transaction = Transaction.query \
                           .filter_by(id=transaction_id) \
                           .first_or_404()

  customer = current_user.account

  # validate transaction
  valid, err = validate_transaction(transaction, customer)
  if not valid:
    print(err)
    return jsonify(success=False, error=err['message']), err['code']

  # assume all products are from the same vendor
  # TODO need to revisit this
  vendor = transaction.products[0].vendor

  try:
    if customer.stripe_id is None:
      s_customer = stripe.Customer.create(
          email=transaction.customer.user.email,
          card=data['token']
      )
      customer.stripe_id = s_customer.id
      db.session.add(customer)
      db.session.commit()
    else:
      s_customer = stripe.Customer.retrieve(customer.stripe_id)

    stripe.Charge.create(
      customer=s_customer.id,
      amount=transaction.total,
      currency='usd',
      description='Gradient transaction for {}'.format(vendor.slug)
    )

    transaction.status = Transaction.Status.SUCCESS
    db.session.add(transaction)
    db.session.commit()
  except (CardError, InvalidRequestError) as e:
    print("Exception: called 'pay'")
    return jsonify(success=False, error=e._message), 400

  # TODO validate that these are external urls in vendor form
  # TODO is it ok to include url params like this? - NOT OKAY

  url = vendor.redirect_url
  url = set_query_parameter(url, 'txid', transaction.uuid)
  url = set_query_parameter(url, 'vid', vendor.id)
  # return redirect('{}?txid={}&vid={}'.format(
  #   vendor.redirect_url, transaction.uuid, vendor.id))
  return redirect(url)


@bp.route('/validate', methods=['POST'])
@cross_origin()
def validate():
  '''
  This checks that a transaction was successfully
  completed. Vendors use this to ensure that the customer
  completed the checkout process. (see gradient.js)
  '''
  data = request.get_json()
  id = data['txid']
  key = data['txkey']
  transaction = Transaction.query.filter_by(uuid=id).first_or_404()

  # check that the supplied secret key is valid for the transaction
  if not transaction.validate_key(key):
    return jsonify(success=False, message='Transaction key is invalid.')

  # check that the transaction status is SUCCESS
  elif transaction.status != Transaction.Status.SUCCESS:
    return jsonify(success=False, message='Transaction was not successfully completed.')

  else:
    return jsonify(success=True)


@bp.route('/vendor_name', methods=['GET'])
@cross_origin()
def vendor_name():
  '''
  This gets the vendors name from the vendor's id
  '''
  vendor_name = 'vendor name'
  vendor_id = request.args.get('vendor_id')
  vendor = Vendor.query.filter_by(id=vendor_id).first_or_404()
  return vendor.company_name

