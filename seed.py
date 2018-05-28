
"""
Generate some seed data to use on the dev site.
"""

import random
import argparse
from tests import factory
from gradient import create_app


if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--username', 
          help='prefix for customer & vendor usernames')
  parser.add_argument('-r', '--randomize-username', action='store_true',
          help='generate a random customer and vendor')
  parser.add_argument('-p', '--password', 
          help='password for customer & vendor')
  args = parser.parse_args()

  username_prefix = args.username
  password = args.password
  
  # override username_prefix with a random string (if -r flag is used)
  if args.randomize_username:
    username_prefix = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
    password = 'pass123!'

  app = create_app()
  with app.app_context():
    
    # create customer account
    email = username_prefix + '_customer@test.com'
    customer = factory.create_customer(
        app, email=email, password=password)
    print('created customer: {}/{}'.format(email, password))

    # create vendor account
    email = username_prefix + '_vendor@test.com'
    vendor = factory.create_vendor(
        app, email=email, password=password)
    print('created vendor: {}/{}'.format(email, password))

    # products = [factory.create_product(
    #     app,
    #     vendor,
    #     sku=str(i)
    # ) for i in range(5)]

    # transaction = factory.create_transaction(app, customer)

    # for p in products:
    #     transaction.add_product(p, 20, 10)

    # app.db.session.add(transaction)
    # app.db.session.commit()
