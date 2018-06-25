from functools import wraps
from flask_security import login_required, current_user
from flask import (
  Blueprint, redirect, url_for, current_app, flash
)
from ..datastore import db

bp = Blueprint('user', __name__)


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

