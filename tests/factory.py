import random
from flask_security.confirmable import confirm_user
from flask_security.registerable import register_user
from gradient.user import User, Address
from gradient.vendor import Vendor
from gradient.product import Product
from gradient.customer import Customer, MaritalStatus
from gradient.transaction import Transaction


def create_user(app, email=None, password='test'):
  email = email or 'test+{}@hellovelocity.com'.format(''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10)))

  # TODO - use register_user to get user otherwise password wont be encrypted
  # data = {
  #   'email': email,
  #   'password': password,
  #   'first_name': 'some_firstname',
  #   'last_name': 'some_lastname'
  # }
  # user = register_user(**data)
  user = User(
    email=email,
    password=password,
    first_name='some_firstname',
    last_name='some_lastname',
    active=True
  )
  address = Address(
    street='17 Meacham Rd, Apt 1',
    city='Cambridge',
    state_code='MA',
    zip_code='12345'
  )
  user.address = address
  confirm_user(user)
  app.db.session.add(user)
  app.db.session.commit()
  return user


def create_customer(app, email=None, password='test'):
  user = create_user(app, email, password)
  customer = Customer(
    user=user,
    individual_income=100000,
    household_income=0,
    marital_status=MaritalStatus.NOT_MARRIED,
    dependents=0
  )
  app.db.session.add(customer)
  app.db.session.commit()
  return customer


def create_vendor(app, user=None, email=None, password='test'):
  user = create_user(app, email, password)
  vendor = Vendor(
    user=user,
    company_name="vendor_test_name",
    redirect_url="http://www.hellovelocity.com"
  )
  app.db.session.add(vendor)
  app.db.session.commit()
  return vendor


def create_product(app, vendor, sku='123'):
  product = Product(sku=sku, vendor=vendor)
  app.db.session.add(product)
  app.db.session.commit()
  return product


def create_transaction(app, customer):
  transaction = Transaction(
    customer=customer,
    status=Transaction.Status.OPEN)
  app.db.session.add(transaction)
  app.db.session.commit()
  return transaction

