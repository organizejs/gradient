from sqlalchemy.ext.declarative import as_declarative, declared_attr
from ..datastore import db, AuditableMixin, AuditAction, AuditMixin
from ..product import Product

class GradientPricePropertiesMixin():
  price     = db.Column(db.Integer(), nullable=False) # in cents
  max_price = db.Column(db.Integer(), nullable=False) # in cents
  min_price = db.Column(db.Integer(), nullable=False) # in cents

  @declared_attr
  def transaction_id(cls):
    return db.Column(db.Integer(), 
                     db.ForeignKey('transaction.id'))
                     # primary_key=True)

  @declared_attr
  def product_id(cls):
    return db.Column(db.Integer(), 
                     db.ForeignKey('product.id'))
                     # primary_key=True) 


class GradientPrice(db.Model, GradientPricePropertiesMixin, AuditableMixin):
  id          = db.Column(db.Integer(), primary_key=True)
  transaction = db.relationship('Transaction', 
                                backref=db.backref('gradient_prices', 
                                                   lazy='dynamic'))
  product     = db.relationship('Product', 
                                backref=db.backref('gradient_prices', 
                                                   lazy='dynamic'))

  @property
  def audit_class(self):
    return GradientPriceAudit

  @property
  def properties_mixin(self):
    return GradientPricePropertiesMixin


class GradientPriceAudit(db.Model, GradientPricePropertiesMixin, AuditMixin):
  __tablename__ = 'gradient_price_audit'



