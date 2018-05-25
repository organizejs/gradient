from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
from abc import abstractmethod
from sqlalchemy.event import listen

db = SQLAlchemy(session_options={'autoflush': False})


'''
--------
Auditing
--------

All tables in Gradient should be auditable - which means that 
all activity that happens in each table must be logged somewhere. 
The following shows how to make things auditable in gradient

In order to make a table 'auditable' we will use the classes 
below: AuditAction, AuditMixin & AuditableMixin

The AuditMixin is the mixin to add to the actual audit table. 
The AuditableMixin is the mixin to add the table you with to make 
auditable.

Ex

Lets use the Product table as an example...

To use the below classes to make the Product table
auditable, we need to use the following:
  - ProductPropertiesMixin
  - Product 
  - ProductAudit

Both the Product and the ProductAudit must use the inherit the 
db.model as they are actual postgres tables.

class ProductPropertiesMixin():
  property_a = db.Column(...)
  property_b = db.Column(...)

class Product(db.Model, ProductPropertiesMixin, AuditableMixin):
  id = db.Column(db.Integer(), primary_key=True)

  @property
  def audit_class(self):
    return ProductAudit

  @property
  def properties_mixin(self):
    return ProductPropertiesMixin

class ProductAudit(db.Model, ProductPropertiesMixin, AuditMixin):
  __tablename__ = 'product_audit'

'''

class AuditAction(Enum):
  INSERT = 0
  UPDATE = 1


class AuditMixin():
  '''
  this is a mixin for the audit classes
  '''
  timestamp = db.Column(db.DateTime(), 
                        primary_key=True, 
                        default=datetime.utcnow)
  id        = db.Column(db.Integer())
  action    = db.Column(db.Enum(AuditAction),
                        default=AuditAction.INSERT,
                        nullable=False)

class AuditableMixin():
  '''
  this is a mixin for classes that should be auditable
  '''
  @property
  @abstractmethod
  def audit_class(self):
    pass
 
  @property
  @abstractmethod
  def properties_mixin(self):
    pass
  
  @classmethod
  def __declare_last__(cls):
    listen(cls, 'after_update', cls.log_update)
    listen(cls, 'after_insert', cls.log_insert)
 
  @staticmethod
  def log_update(mapper, connection, target):
    target.add_audit_row(mapper, connection, target, \
      target.audit_class, target.properties_mixin, AuditAction.UPDATE)
 
  @staticmethod
  def log_insert(mapper, connection, target):
    target.add_audit_row(mapper, connection, target, \
      target.audit_class, target.properties_mixin, AuditAction.INSERT)
 
  @staticmethod
  def add_audit_row(mapper, connection, target, \
    audit_class, properties_mixin, action):
    '''
    Adds new row to Audit table- the fields are
    dynamically built using the attributes in the
    correlating properties class
    '''

    values = {
      'id': target.id,
      'action': action
    }

    for p in dir(properties_mixin):
      if not p.startswith('_'):
        values[p] = getattr(target, p)

    ins = audit_class.__table__.insert().values(values)
    connection.execute(ins)

  @property
  def updated_at(self):
    return self.audit_class.query.filter_by(id=self.id) \
      .order_by('timestamp desc').first().timestamp

  @property
  def created_at(self):
    return self.audit_class.query \
      .filter_by(id=self.id, action=AuditAction.INSERT) \
      .first().timestamp


