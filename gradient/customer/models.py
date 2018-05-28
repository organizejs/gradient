from datetime import datetime
from ..datastore import db, AuditAction, AuditMixin, AuditableMixin
from ..user import HasUser
from ..util import FormEnum


class MaritalStatus(FormEnum):
  NOT_MARRIED = 0
  MARRIED = 1


class CustomerPropertiesMixin():
  individual_income = db.Column(db.Integer()) # in cents
  household_income  = db.Column(db.Integer()) # in cents
  marital_status    = db.Column(db.Enum(MaritalStatus), 
                                default=MaritalStatus.NOT_MARRIED, 
                                nullable=False)
  dependents        = db.Column(db.Integer(), default=0)
  signature         = db.Column(db.String())
  stripe_id         = db.Column(db.String(255))


class Customer(db.Model, HasUser, CustomerPropertiesMixin, AuditableMixin):
  id = db.Column(db.Integer(), primary_key=True)

  @property
  def audit_class(self):
    return CustomerAudit

  @property
  def properties_mixin(self):
    return CustomerPropertiesMixin


class CustomerAudit(db.Model, CustomerPropertiesMixin, AuditMixin):
  __tablename__ = 'customer_audit'

