from functools import wraps
from flask import (
    Blueprint, jsonify, redirect, render_template, 
    abort, url_for, flash,
)
from flask_security import current_user, login_user
from flask_security.registerable import register_user
from flask_security.decorators import anonymous_user_required
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


@bp.route('/account/settings/subscribe')
@customer_required
def subscribe():
    '''
    Subscribe Customer
    '''
    current_user.update_subscribe(True);
    db.session.commit()
    flash('Thank you for subscribing.')
    return redirect(url_for('customer.settings'))


@bp.route('/account/settings/unsubscribe')
@customer_required
def unsubscribe():
    '''
    Unsubscribe Customer
    '''
    current_user.update_subscribe(False);
    db.session.commit()
    flash('You have successfully unsubscribed.')
    return redirect(url_for('customer.settings'))


@bp.route('/register/validate/signature', methods=['POST'])
def validate_signature():
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
    '''
    Validation for customer details
    Validate details form
    '''
    form = DetailsForm(csrf_enabled=False)
    if form.validate_on_submit():
        return jsonify(success=True)
    else:
        return jsonify(success=False, errors=form.errors)


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

        # create address model out of form
        address = Address()
        form.populate_obj(address)
        current_user.address = address
        current_user.update_subscribe(data.get('subscribe'));

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

