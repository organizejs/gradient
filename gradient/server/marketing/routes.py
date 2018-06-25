from functools import wraps
from flask import (
  g, Blueprint, render_template, jsonify, request, 
  redirect, url_for, session, current_app, flash
)
from flask_security.decorators import anonymous_user_required
from datetime import datetime
from .forms import SubscribeForm
from ..mailchimp import mc
from ..datastore import db

bp = Blueprint('main', __name__)


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
  return render_template('marketing/faq.html')


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
  return render_template('marketing/index.html')


