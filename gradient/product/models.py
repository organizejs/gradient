from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from ..datastore import db, AuditAction, AuditMixin, AuditableMixin


class ProductPropertiesMixin():
  name       = db.Column(db.String())  
  max_price  = db.Column(db.Integer()) 
  min_price  = db.Column(db.Integer()) 
  sku        = db.Column(db.String(), nullable=False, index=True)
  image_url  = db.Column(db.Unicode())
  properties = db.Column(JSON())
  active     = db.Column(db.Boolean(), default=True)

  @declared_attr
  def vendor_id(cls):
    return db.Column(db.Integer(), 
                     db.ForeignKey('vendor.id'), 
                     index=True)


class Product(db.Model, ProductPropertiesMixin, AuditableMixin):
  id           = db.Column(db.Integer(), primary_key=True)
  vendor       = db.relationship('Vendor', 
                                 backref=db.backref('products'))
  transactions = association_proxy('gradient_prices', 'transaction')
  # __table_args__ = (db.Index('sku_vendor_index', 'sku', 'vendor_id'), )

  @property
  def audit_class(self):
    return ProductAudit

  @property
  def properties_mixin(self):
    return ProductPropertiesMixin

  def deactivate(self):
    '''
    Use as proxy for deletion
    '''
    self.active = False
    db.session.commit()

  def reactivate(self):
    '''
    Use to reactivate deactivated products
    NOT IN USE (TODO: remove comment when in use)
    '''
    self.active = True
    db.session.commit()


class ProductAudit(db.Model, ProductPropertiesMixin, AuditMixin):
  __tablename__ = 'product_audit'

