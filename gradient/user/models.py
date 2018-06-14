from enum import Enum
from datetime import datetime, timezone
from flask_security import UserMixin, RoleMixin
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from ..datastore import db, AuditAction, AuditMixin, AuditableMixin
from ..mailchimp import mc


# TODO: Not in use
roles_users = db.Table('roles_users',
  db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
  db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


# TODO: Not in use
class Role(db.Model, RoleMixin):
  id          = db.Column(db.Integer(), primary_key=True)
  name        = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


# ===============
# Address
# ===============

class AddressPropertiesMixin():
  street      = db.Column(db.String)
  city        = db.Column(db.String)
  state_code  = db.Column(db.Unicode(2))
  zip_code    = db.Column(db.Unicode(16))


class Address(db.Model, AddressPropertiesMixin, AuditableMixin):
  id = db.Column(db.Integer(), primary_key=True)

  @property
  def audit_class(self):
    return AddressAudit

  @property
  def properties_mixin(self):
    return AddressPropertiesMixin


class AddressAudit(db.Model, AddressPropertiesMixin, AuditMixin):
  __tablename__ = 'address_audit'


# ===============
# User
# ===============

class UserPropertiesMixin():
  first_name   = db.Column(db.Unicode(255), nullable=False)
  last_name    = db.Column(db.Unicode(255), nullable=False)
  email        = db.Column(db.String(255)) #, unique=True)
  active       = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  password     = db.Column(db.String(255))
  account_id   = db.Column(db.Integer())
  account_type = db.Column(db.String(50))
  subscribed   = db.Column(db.Boolean(), default=False)

  @declared_attr
  def address_id(cls):
    return db.Column(db.Integer(),
                     db.ForeignKey('address.id'),
                     index=True)


class User(db.Model, UserPropertiesMixin, AuditableMixin, UserMixin):
  id      = db.Column(db.Integer(), primary_key=True)
  address = db.relationship('Address', 
                            backref=db.backref('user', uselist=False))
  roles   = db.relationship('Role', 
                            secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

  @property
  def audit_class(self):
    return UserAudit

  @property
  def properties_mixin(self):
    return UserPropertiesMixin

  @property
  def account(self):
    return getattr(self, 'parent_{}'.format(self.account_type))

  @validates('email')
  def validate_email(self, key, email):
    '''
    assert uniqueness + assert email contains '@'
    '''
    assert '@' in email  
    assert self.query.filter_by(email=email).count() == 0
    return email

  def update_subscription(self, subscribe):
    ''' 
    update subscription on mailchimp
    '''
    self.subscribed = subscribe 
    if self.subscribed:
      mc.add_or_update_user( \
        email=self.email, \
        is_registered=True, \
        status='subscribed', \
        first_name=self.first_name, \
        last_name=self.last_name)
    else:
      mc.add_or_update_user( \
        email=self.email, \
        is_registered=True, \
        status='unsubscribed', \
        first_name=self.first_name, \
        last_name=self.last_name)


class UserAudit(db.Model, UserPropertiesMixin, AuditMixin):
  __tablename__ = 'user_audit'


# ===============
# Setup Customer / Vendor Relationship
# ===============

class HasUser():
  pass


@db.event.listens_for(HasUser, 'mapper_configured', propagate=True)
def setup_listener(mapper, class_):
  '''
  Sets the database up so that User objects can have either a
  Vendor or a Customer associated with them, as an `account`.

  Ex. 
  vendor = Vendor(user=current_user, ...)
  '''
  name = class_.__name__
  account_type = name.lower()
  class_.user = db.relationship(
    User,
    primaryjoin=db.and_(
        class_.id == db.foreign(db.remote(User.account_id)),
        User.account_type == account_type
    ),
    backref=db.backref(
        'parent_{}'.format(account_type),
        primaryjoin=db.remote(class_.id) == db.foreign(User.account_id)
    ),
    uselist=False)

  @db.event.listens_for(class_.user, 'set')
  def set_user(target, value, old_value, initiator):
    value.account_type = account_type


