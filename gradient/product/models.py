from ..datastore import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.associationproxy import association_proxy


class Product(db.Model):
    '''
    Notes:
    - different vendors can products with the same SKU
    - a single vendor cannot have different products with the same SKU
    - a single vendor can have multiple products with the same name
    '''

    id             = db.Column(db.Integer(), primary_key=True)
    name           = db.Column(db.String())  
    max_price      = db.Column(db.Integer()) 
    min_price      = db.Column(db.Integer()) 
    sku            = db.Column(db.String(), nullable=False, index=True)
    image_url      = db.Column(db.Unicode())
    properties     = db.Column(JSON())
    created_at     = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime(), 
                               default=datetime.utcnow, 
                               onupdate=datetime.utcnow)
    vendor         = db.relationship('Vendor', 
                                     backref=db.backref('products'))
    vendor_id      = db.Column(db.Integer(), 
                               db.ForeignKey('vendor.id'), 
                               index=True)
    transactions   = association_proxy('gradient_prices', 'transaction')

    __table_args__ = (db.Index('sku_vendor_index', 'sku', 'vendor_id'), )
