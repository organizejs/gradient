from os import environ
from .base import BaseConfig

class Config(BaseConfig):
  DEBUG = False
  DEBUG_ASSETS = False

# load other config vars from env
# assumes the env vars are prefixed with `FLASK_`
keys = [
  'SECRET_KEY',
  'STRIPE_SECRET_KEY',
  'MAIL_SERVER',
  'MAIL_USERNAME',
  'MAIL_PASSWORD',
  'MAIL_DEFAULT_SENDER',
  'SQLALCHEMY_DATABASE_URI',
  'SECURITY_PASSWORD_SALT',
  'SECURITY_EMAIL_SENDER',
  'STRIPE_SECRET_KEY',
  'STRIPE_PUBLIC_KEY',
  'MAILCHIMP_KEY',
  'MAILCHIMP_USERNAME',
  'MAILCHIMP_UNREGISTERED_LIST_ID',
  'MAILCHIMP_REGISTERED_LIST_ID',
  'SENTRY_DSN',
  'TX_SECRET_KEY'
]
for k in keys:
  setattr(Config, k, environ['FLASK_{}'.format(k)])
