from stripe.error import CardError, InvalidRequestError
from flask_cors import cross_origin
from flask_security import login_required, current_user
from flask import (
  Blueprint, render_template, jsonify, request, redirect, 
  url_for, session, abort
)
from ..stripe import stripe
from .models import Cart
from ..util import set_query_parameter
from ..product import Product
from ..vendor import Vendor
from ..customer import customer_required
from ..transaction import Transaction
from ..datastore import db

bp = Blueprint('checkout', __name__, url_prefix='/checkout')


@bp.route('/initialize', methods=['POST', 'OPTIONS'])
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
  # get requester url 
  requester_url = request.environ['HTTP_REFERER']

  # get vendor and products from POST body (json)
  data = request.get_json()
  vendor_id = data['vendor_id']
  products = data['products']

  # get vendor, throw error if dne
  vendor = Vendor.query.get_or_404(vendor_id)

  # create Cart & add products
  cart = Cart(vendor=vendor)
  for product in products:
    sku = product['sku']
    quantity = product['quantity']
    cart.add_product(sku, int(quantity))

  # create transaction object with OPEN transaction.status
  current_transaction = Transaction(
    vendor=vendor,
    requester_url=requester_url,
    status=Transaction.Status.OPEN
  )

  # add products to transaction
  current_transaction.add_cart(cart)

  # update db
  db.session.add(current_transaction)
  db.session.commit()

  return jsonify(success=True,
                 key=current_transaction.key,
                 url=url_for('checkout.cart', 
                   txid=current_transaction.uuid, 
                   _external=True))


@bp.route('/cart')
@customer_required
def cart():
  '''
  Displays the cart/checkout page for a customer,
  listing the products they are about to pay for,
  with their respective Gradient prices. 
  
  But first we check if they are the owner of the 
  transaction and that the transaction is still OPEN.
  '''
  # get current transaction
  transaction_uuid = request.args.get('txid', -1) 
  transaction = Transaction.query \
                           .filter_by(uuid=transaction_uuid) \
                           .first_or_404()

  # block if user is not of type customer
  if current_user.account_type != 'customer':
    return 'Not a customer', 400

  # set ownership of transaction to current_user/customer
  if transaction.customer == None:
    # TODO: this has some security implications ideally we set
    #   ownership of this transaction via a session variable
    customer = current_user.account
    transaction.customer = customer

    # validate transaction
    valid, err = transaction.validate_transaction(customer)
    if not valid:
      return err['message'], err['code']

    # add to db
    db.session.add(transaction)
    db.session.commit()

  # get all cards if customer stripe id exists
  cards = None
  if transaction.customer.stripe_customer_id:
    stripe_customer = stripe.client.Customer \
      .retrieve(transaction.customer.stripe_customer_id)
    cards = stripe_customer.sources.all(object='card')

  # if user added new card, get card id in session
  new_card_id = None
  if session.get('new_card_id'):
    new_card_id = session.get('new_card_id')
    session.pop('new_card_id', None)

  # TODO - get gradient price using "price()" and update transaction

  return render_template(
    'checkout/pay.html',
    cards=cards,
    new_card_id=new_card_id,
    requester_url=request.referrer,
    transaction=transaction)


@bp.route('/add_card')
def add_card():
  '''
  '''
  # add request_referrer in case user add cards,
  #   user will need a way to return to the page
  return render_template('checkout/add_card.html', 
                         next=request.referrer)


@bp.route('/pay', methods=['POST'])
@customer_required
def pay():
  '''
  Process payment for a transaction.
  expects the following POSTed form data:
    {
      'transaction_id': uuid,
      'card_id': str
    }

  First, we validate:
    - user is authenticated
    - transaction exists
    - transaction has status of OPEN
    - authenticated user is transaction owner

  if payment is successful, transaction status is set to SUCCESS
  and the user is redirected to the confirmation.html template.

  The confirmation.html will display to the user that the
  transaction was successful and then it will redirect to the
  vendor's redirect url, passing it the transaction_uuid (txid) 
  and the vendor's id (vid).
  
  These 2 params should be used by the vendor to validate the
  transaction was successfully completed (see gradient.js).
  '''

  data = request.form
  card_id = data['card_id']
  txid = data['txid']

  customer = current_user.account

  # verify transaction exists
  transaction = Transaction.query \
                           .filter_by(uuid=txid) \
                           .first_or_404()

  # validate transaction
  valid, err = transaction.validate_transaction(customer)
  if not valid:
    print(err['message'])
    return jsonify(success=False, error=err['message']), err['code']

  # assume all products are from the same vendor
  # TODO need to revisit this
  vendor = transaction.products[0].vendor

  # verify that customer has a stripe id (which is created when adding a card)
  if customer.stripe_customer_id is None:
    msg = "Error: customer does not have a stripe id. Card must be added first"
    print(msg)
    return jsonify(success=False, error=msg), 400

  # verify that customer has card_id / that card_id is valid
  cards = stripe.client.Customer \
    .retrieve(customer.stripe_customer_id) \
    .sources.all(limit=100, object='card') \
    .data
  if card_id not in [card.id for card in cards]:
    msg = "Error: customer does not have card id '%s'."%card_id
    print(msg)
    return jsonify(success=False, error=msg), 400

  # verify that vendor has a valid stripe account
  if not vendor.stripe_is_authorized:
    return jsonify(success=False, \
      error="Vendor does not have an authorized Stripe account"), 400

  try:
    # create charge
    stripe_charge = stripe.client.Charge.create(
      customer=customer.stripe_customer_id,
      source=card_id,
      amount=transaction.total,
      currency='usd',
      description='Gradient transaction for {}'.format(vendor.slug),
      metadata={'transaction_id': transaction.id},
      destination={
        # "amount": 0, # fees that gradient will take
        "account": vendor.stripe_user_id 
      }
    )

    # update db with transaction status & stripe charge id
    transaction.status = Transaction.Status.SUCCESS
    transaction.stripe_charge_id = stripe_charge.id

    # save to db
    db.session.add(transaction)
    db.session.commit()

  except (CardError, InvalidRequestError) as e:
    print("Exception: called 'pay'")
    return jsonify(success=False, error=e._message), 400

  return render_template(
    'checkout/confirmation.html',
    vendor=vendor,
    transaction=transaction)





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

