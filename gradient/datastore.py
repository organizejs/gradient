from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
from abc import abstractmethod
from sqlalchemy.event import listen

db = SQLAlchemy(session_options={'autoflush': False})


# -----------------------
# ---- Auditing Code ----
# -----------------------


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
  - requires that all classes that uses this mixin 
    implements the audit_class & properties_mixin property
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


