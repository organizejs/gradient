from config import Config
from datetime import datetime
from sqlalchemy_utils import EncryptedType
from sqlalchemy.dialects.postgresql import JSON
from ..datastore import db, AuditAction, AuditMixin, AuditableMixin
from ..user import HasUser


class VendorPropertiesMixin():
  slug                   = db.Column(db.Unicode(), index=True, unique=True)
  company_name           = db.Column(db.Unicode(255))
  redirect_url           = db.Column(db.Unicode())
  stripe_is_authorized   = db.Column(db.Boolean())
  stripe_account_resp    = db.Column(EncryptedType(db.String, Config.SECRET_KEY))
  stripe_publishable_key = db.Column(db.String())
  stripe_user_id         = db.Column(db.String())
  stripe_refresh_token   = db.Column(db.String())
  stripe_access_token    = db.Column(EncryptedType(db.String, Config.SECRET_KEY))


class Vendor(db.Model, HasUser, VendorPropertiesMixin, AuditableMixin):
  id = db.Column(db.Integer(), primary_key=True)

  @property
  def audit_class(self):
    return VendorAudit

  @property
  def properties_mixin(self):
    return VendorPropertiesMixin


class VendorAudit(db.Model, VendorPropertiesMixin, AuditMixin):
  __tablename__ = 'vendor_audit'

