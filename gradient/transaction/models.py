from enum import Enum
from uuid import uuid4
from config import Config
from ..datastore import db
from ..product import Product
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.associationproxy import association_proxy

# load Fernet for encrypting keys (see below)
f = Fernet(Config.TX_SECRET_KEY)


class GradientPrice(db.Model):
    id             = db.Column(db.Integer(), 
                               primary_key=True, 
                               autoincrement=True)
    created_at     = db.Column(db.DateTime(), default=datetime.utcnow)
    price          = db.Column(db.Integer(), nullable=False) # in cents
    max_price      = db.Column(db.Integer(), nullable=False) # in cents
    min_price      = db.Column(db.Integer(), nullable=False) # in cents
    product_id     = db.Column(db.Integer(), 
                               db.ForeignKey('product.id'), 
                               primary_key=True) 
    transaction_id = db.Column(db.Integer(), 
                               db.ForeignKey('transaction.id'), 
                               primary_key=True)
    transaction    = db.relationship('Transaction', 
                                     backref=db.backref('gradient_prices', 
                                                        lazy='dynamic'))
    product        = db.relationship(Product, 
                                     backref=db.backref('gradient_prices', 
                                                        lazy='dynamic'))

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


class Transaction(db.Model):
    Status = TransactionStatus

    id          = db.Column(db.Integer(), 
                            primary_key=True)
    uuid        = db.Column(UUID(as_uuid=True), 
                            index=True, 
                            default=uuid4)
    created_at  = db.Column(db.DateTime(), 
                            default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime(), 
                            default=datetime.utcnow, 
                            onupdate=datetime.utcnow)
    properties  = db.Column(JSON())
    customer    = db.relationship('Customer', 
                                  backref=db.backref('transactions'))
    customer_id = db.Column(db.Integer(), 
                            db.ForeignKey('customer.id'))
    vendor      = db.relationship('Vendor', 
                                  backref=db.backref('transactions'))
    vendor_id   = db.Column(db.Integer(), 
                            db.ForeignKey('vendor.id'),
                            nullable=False)
    status      = db.Column(db.Enum(TransactionStatus), 
                            default=TransactionStatus.OPEN, 
                            nullable=False)
    products    = association_proxy('gradient_prices', 'product')

    @property
    def total(self):
        return sum(gp.price for gp in self.gradient_prices)

    def add_product(self, product, price, max_price, min_price):
        self.gradient_prices \
            .append(GradientPrice(product=product, 
                                  price=price, 
                                  max_price=max_price,
                                  min_price=min_price))

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
