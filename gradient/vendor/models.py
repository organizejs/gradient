from config import Config
from datetime import datetime
from sqlalchemy_utils import EncryptedType
from ..datastore import db, AuditAction, AuditMixin, AuditableMixin
from ..user import HasUser


class VendorPropertiesMixin():
  created_at   = db.Column(db.DateTime(), default=datetime.utcnow)
  updated_at   = db.Column(db.DateTime(), 
                           default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
  slug         = db.Column(db.Unicode(), index=True, unique=True)
  company_name = db.Column(db.Unicode(255))
  stripe_sk    = db.Column(EncryptedType(db.String, Config.SECRET_KEY))
  stripe_pk    = db.Column(EncryptedType(db.String, Config.SECRET_KEY))
  redirect_url = db.Column(db.Unicode())


class Vendor(db.Model, HasUser, VendorPropertiesMixin, AuditableMixin):
  id = db.Column(db.Integer(), primary_key=True)

  @property
  def audit_class(self):
    return VendorAudit

  @property
  def properties_mixin(self):
    return VendorPropertiesMixin

  def render_stripe_sk(self):
      return '****{}'.format(self.stripe_sk[-4:])

  def render_stripe_pk(self):
      return '****{}'.format(self.stripe_pk[-4:])


class VendorAudit(db.Model, VendorPropertiesMixin, AuditMixin):
  __tablename__ = 'vendor_audit'

