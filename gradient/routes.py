from functools import wraps
from flask_security import login_required, current_user
from flask import (
    g, Blueprint, render_template, jsonify, request, 
    redirect, url_for, session, current_app, flash
)
from flask_security.decorators import anonymous_user_required
from datetime import datetime
from .datastore import db
from .forms import SubscribeForm
from .mailchimp import mc

bp = Blueprint('main', __name__)


@bp.before_request
def update_last_seen():
    '''
    Update user's last_seen_on field
    '''
    if current_user.is_authenticated:
        current_user.update_last_seen()
        db.session.commit()


@bp.route('/subscribe', methods=['POST'])
def subscribe():
    '''
    Validate subscribe form and add subscriber
    Returns a json formatted:
    {
        success: <bool>,
        errors: <str> (error to display)
    }
    '''
    form = SubscribeForm(request.form, csrf_enabled=False)
    if form.validate():
        mc.add_or_update_user(form.email.data)
        return jsonify(success=True)
    else:
        return jsonify(success=False, errors=form.errors["email"][0])


@bp.route('/faq')
def faq():
    '''
    Renders faq page
    '''
    return render_template('faq.html')


@bp.route('/docs')
def docs():
    '''
    Redirect to docs
    '''
    return redirect(url_for('docs.home'))


@bp.route('/')
def index():
    '''
    Renders home page
    '''
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return render_template('index.html')


@bp.route('/account')
@login_required
def account():
    '''
    Redirect to 'account' page depending on user account type
    '''
    if current_user.account_type == 'customer':
        if current_user.account.individual_income is None \
                and current_user.account.household_income is None:
            return redirect(url_for('customer.onboarding'))
        else:
            return redirect(url_for('customer.account'))

    if current_user.account_type == 'vendor':
        return redirect(url_for('vendor.account'))

