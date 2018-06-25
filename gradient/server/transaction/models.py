from typing import Dict
from enum import Enum
from uuid import uuid4
from config import Config
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from ..datastore import db, AuditableMixin, AuditAction, AuditMixin
from ..product import Product
from ..gradient_price import GradientPrice

# load Fernet for encrypting keys (see below)
f = Fernet(Config.TX_SECRET_KEY)


class TransactionStatus(Enum):
  OPEN = 0
  SUCCESS = 1
  FAILURE = 2

  @classmethod
  def desc(cls, status):
    if cls == cls.OPEN:
      return 'User has clicked "checkout" and is \
                selecting/entering payment info'
    elif cls == cls.SUCCESS:
      return 'User has successfully paid'
    elif cls == cls.FAILURE:
      return 'Payment failed'
    else:
      return 'UNKNOWN'


class TransactionPropertiesMixin():
  uuid             = db.Column(UUID(as_uuid=True), index=True, default=uuid4)
  requester_url    = db.Column(db.String())
  properties       = db.Column(JSON())
  status           = db.Column(db.Enum(TransactionStatus), 
                            default=TransactionStatus.OPEN, 
                            nullable=False)
  stripe_charge_id = db.Column(db.String()) # the stripe 'Charge' id

  @declared_attr
  def customer_id(self):
    return db.Column(db.Integer(), db.ForeignKey('customer.id'))

  @declared_attr
  def vendor_id(self):
    return db.Column(db.Integer(), db.ForeignKey('vendor.id'), nullable=False)


class Transaction(db.Model, TransactionPropertiesMixin, AuditableMixin):
  Status = TransactionStatus

  id       = db.Column(db.Integer(), primary_key=True)
  products = association_proxy('gradient_prices', 'product')
  customer = db.relationship('Customer', 
                             backref=db.backref('transactions'))
  vendor   = db.relationship('Vendor', 
                             backref=db.backref('transactions'))

  @property
  def audit_class(self):
    return TransactionAudit 

  @property
  def properties_mixin(self):
    return TransactionPropertiesMixin

  @property
  def total(self):
    return sum(gp.price for gp in self.gradient_prices)

  @property
  def key(self):
    '''
    Generates an encrypted key based off of this transaction's UUID
    '''
    return f.encrypt(str(self.uuid).encode('utf8')).decode('utf8')

  def validate_key(self, key):
    '''
    Asserts that the supplied key, when decrypted, matches this
    transaction's UUID
    '''
    return f.decrypt(key.encode('utf8')).decode('utf8') == str(self.uuid)

  def validate_transaction(self, customer: 'Customer') -> (bool, dict):
    '''
    validate that transaction is OPEN
    if 'customer' param is passed in, validate that customer is correct
    '''
    # check that transaction is OPEN
    if self.status != self.Status.OPEN:
      return False, { 'message': 'Transaction is not open', 'code': 403 }

    # check that customer is correct
    if customer:
      if self.customer != customer:
        return False, { 'message': 'Not owner of transaction', 'code': 401 }

    return True, {}

  def add_cart(self, cart: 'Cart'):
    '''
    add a cart of products to the transaction
    '''

    for cart_item in cart.items:
      product = cart_item.product
      quantity = cart_item.quantity

      # add gradient price for each product
      gradient_price = GradientPrice(transaction=self,
                                     product=product,
                                     quantity=quantity,
                                     price=100,
                                     max_price=None,
                                     min_price=None)


class TransactionAudit(db.Model, AuditMixin, TransactionPropertiesMixin):
  __tablename__ = 'transaction_audit'

