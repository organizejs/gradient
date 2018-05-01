import stripe
from stripe.error import CardError, InvalidRequestError
from flask_cors import cross_origin
from flask_security import login_required, current_user
from flask import (
    Blueprint, render_template, jsonify, request, redirect, 
    url_for, session, current_app,
)
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
        "products": [
        {
            "id": "<product_0_id>",
            "max_price": "<product_0_max_price>",
            "min_price": "<product_0_min_price>",
            "name": "<product_0_name>",
            "sku": "<product_0_sku>",
            "image_url": "<product_0_image_url>",
            "properties": "..."
        },
        {
            "id": "<product_1_id>",
            "max_price": "<product_1_max_price>",
            "min_price": "<product_1_min_price>",
            "name": "<product_1_name>",
            "sku": "<product_1_sku>",
            "image_url": "<product_1_image_url>",
            "properties": "..."
        },
        ...] }

    1. create transaction object with transaction state OPEN
    2. use financial model to compute price for user
    3. create gradient_price object(s) with computed price
    4. render payment page with computed price
    '''
    user = None

    # get vendor and products from POST body (json)
    checkout_content = request.get_json()
    vendor_id = checkout_content['vendor_id']
    vendor = Vendor.query.get_or_404(vendor_id)
    products = checkout_content['products']

    # create transaction object with OPEN transaction.status
    current_transaction = Transaction(
        customer=user,
        vendor=vendor,
        status=Transaction.Status.OPEN)
    db.session.add(current_transaction)
    db.session.commit()

    # calculate price for each product
    for p in products:
        # add product if not exist
        product = Product.query \
            .filter_by(sku=p['sku'], vendor=vendor) \
            .first()

        if product is None:
            product = Product(vendor=vendor,
                              sku=p['sku'], 
                              max_price=p['max_price'],
                              min_price=p['min_price'],
                              name=p['name'],
                              image_url=p['image_url'])
            db.session.add(product)
            db.session.commit()

        # TODO if product exists,
        # but max_income/min_income is different,
        # how should we handle this case?

        # get gradient price
        gradient_price = price(user, product)

        # update transaction with prices
        current_transaction \
            .add_product(product, 
                         gradient_price, 
                         p['max_price'],
                         p['min_price'])

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
    
    But firs we check if they are the owner of the 
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
    elif current_user.account_type != 'customer':
        return 'Not a customer', 400

    else:
        # set ownership of transaction to current_user/customer
        # TODO 
        #   this has some security implications ideally we set
        #   ownership of this transaction via a session variable
        customer = current_user.account
        transaction.customer = customer
        db.session.add(transaction)
        db.session.commit()

    if transaction.customer is None:
        if transaction.id in session.get('_tids', []):
            # NOTE added customer ref here
            customer = current_user.account
            transaction.customer = customer
            db.session.add(transaction)
            db.session.commit()

    valid, err = validate_transaction(transaction, customer)
    if not valid:
        return err['message'], err['code']

    return render_template(
            'checkout.html',
            transaction=transaction,
            logged_in=True)


def validate_transaction(transaction, user):
    '''
    Validates a transaction for a given user
    '''
    # check that transaction is OPEN
    if transaction.status != Transaction.Status.OPEN:
        return False, {'message': 'Transaction is not open', 'code': 403}

    # check that authenticated user is transaction owner
    if transaction.customer != user:
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
    #     return max_price
    # else:
    #     m = (max_price - min_price)/(vendor.min_income - vendor.max_income)
    #     return min_price + (m*(user.individual_income - vendor.max_income))
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
    # TODO is it ok to include url params like this?
    return redirect('{}?txid={}&vid={}'.format(
        vendor.redirect_url, transaction.uuid, vendor.id))


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

