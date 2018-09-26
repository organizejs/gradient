from config import Config
from flask import Flask
from flask_mail import Mail
from flask_babel import Babel
from flask_migrate import Migrate
from flask_assets import Environment, Bundle
from flask_security import SQLAlchemyUserDatastore, Security
from flask_misaka import Misaka
from raven.contrib.flask import Sentry
from datetime import datetime
from hashlib import md5

from .server import db, mc, stripe
from .server import vendor, customer, checkout, docs, user, marketing


def _generate_assets(app):
  '''
  Helper function to generate static assets
  - /assets/js/gen/main.js
  - /assets/css/gen/style.css
  '''
  assets = Environment(app)

  css = Bundle('css/style.sass',
              #filters='sass,cssmin',
              filters='sass',
              depends=[
                  'css/*.sass',
                  'css/**/*.sass',
                  'css/**/**/*.sass'
              ],
              output='css/gen/style.css')

  js = Bundle('js/*.js',
              'js/modules/*.js',
              #filters='jsmin',
              depends=[
                  'js/*.js',
                  'js/**/*.js',
                  'js/**/**/*.js'
              ],
              output='js/gen/main.js')

  assets.register('css_all', css)
  assets.register('js_all', js)

  app.config['JS_URLS'] = assets['js_all'].urls
  app.config['CSS_URLS'] = assets['css_all'].urls

  return app


def create_app(
    package_name=__name__,
    static_folder='client/static',
    template_folder='client/templates',
    **config_overrides):
  '''
  Main function to creaet Gradient App
  '''

  static_url_path = '/assets'
  
  # =======================================
  # setup app and get properties from config
  # =======================================
  app = Flask(package_name,
              static_url_path=static_url_path,
              static_folder=static_folder,
              template_folder=template_folder)

  app.config.from_object(Config)

  # =======================================
  # setup stripe client 
  # =======================================
  stripe.set_connect_id(app.config['STRIPE_CONNECT_CLIENT_ID'])

  # =======================================
  # load stripe credentials
  # =======================================
  stripe.set_secret_key(app.config['STRIPE_SECRET_KEY'])

  # =======================================
  # load mailchimp credentials
  # =======================================
  mc.set_credentials(app.config['MAILCHIMP_USERNAME'], app.config['MAILCHIMP_KEY'])
  mc.set_unregistered_list_id(app.config['MAILCHIMP_UNREGISTERED_LIST_ID'])
  mc.set_registered_list_id(app.config['MAILCHIMP_REGISTERED_LIST_ID'])

  # =======================================
  # Apply overrides
  # =======================================
  app.config.update(config_overrides)

  # =======================================
  # Initialize the database and 
  # declarative Base class
  # =======================================
  db.init_app(app)
  Migrate(app, db)
  app.db = db

  # =======================================
  # Setup security
  # =======================================
  app.user_db = SQLAlchemyUserDatastore(db, user.User, user.Role)
  Security(app, app.user_db)

  app.mail = Mail(app)
  Babel(app)
  Misaka(app, 
         fenced_code=True,
         space_headers=True)

  # =======================================
  # Setup asset generation
  # =======================================
  generated = False

  if app.debug:
    # in debug mode, always re-generate assets
    app = _generate_assets(app)  
  else:
    if not generated:
      # check if assets (/js/gen/main.js, etc) 
      # are generated, if not, then generate
      app = _generate_assets(app)
      generated = True
    else:
      # hash generated assets (avoid browser caching)
      hash = md5(datetime.utcnow().isoformat().encode('utf8')).hexdigest()[:10]
      app.config['JS_URLS'] = lambda: ['{}/js/gen/main.js?{}'.format(static_url_path, hash)]
      app.config['CSS_URLS'] = lambda: ['{}/css/gen/style.css?{}'.format(static_url_path, hash)]

  # =======================================
  # Create the database tables.
  # Flask-SQLAlchemy needs to know which
  # app context to create the tables in.
  # =======================================
  with app.app_context():
    db.configure_mappers()
    db.create_all()

  # =======================================
  # Register blueprints
  # =======================================
  app.register_blueprint(marketing.bp)
  app.register_blueprint(user.bp)
  app.register_blueprint(vendor.bp)
  app.register_blueprint(customer.bp)
  app.register_blueprint(checkout.bp)
  app.register_blueprint(docs.bp)
  
  # =======================================
  # Setup Sentry
  # =======================================
  if not app.debug and 'SENTRY_DSN' in app.config:
    Sentry(app, dsn=app.config['SENTRY_DSN'])

  return app

