from enum import Enum
from ..datastore import db
from ..mailchimp import mc
from datetime import datetime, timezone
from flask_security import UserMixin, RoleMixin


# TODO: Not in use
roles_users = db.Table('roles_users',
  db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
  db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


# TODO: Not in use
class Role(db.Model, RoleMixin):
  id          = db.Column(db.Integer(), primary_key=True)
  name        = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


class HasUser():
  pass


class Address(db.Model):
  id          = db.Column(db.Integer(), primary_key=True)
  street      = db.Column(db.String)
  city        = db.Column(db.String)
  state_code  = db.Column(db.Unicode(2))
  zip_code    = db.Column(db.Unicode(16))


class User(db.Model, UserMixin):
  id           = db.Column(db.Integer(), primary_key=True)
  created_at   = db.Column(db.DateTime(), 
                           default=datetime.utcnow)
  updated_at   = db.Column(db.DateTime(), 
                           default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
  first_name   = db.Column(db.Unicode(255), nullable=False)
  last_name    = db.Column(db.Unicode(255), nullable=False)
  email        = db.Column(db.String(255), unique=True)
  active       = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  password     = db.Column(db.String(255))
  account_id   = db.Column(db.Integer())
  account_type = db.Column(db.String(50))
  subscribed   = db.Column(db.Boolean(), default=False)
  address_id   = db.Column(db.Integer(),
                           db.ForeignKey('address.id'))
  address      = db.relationship('Address', 
                                 backref=db.backref('user', uselist=False))
  roles        = db.relationship('Role', 
                                 secondary=roles_users,
                                 backref=db.backref('users', lazy='dynamic'))

  
  def update_subscribe(self, subscribe):
    self.subscribe = subscribe 
    if self.subscribe:
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

  @property
  def account(self):
    return getattr(self, 'parent_{}'.format(self.account_type))


@db.event.listens_for(HasUser, 'mapper_configured', propagate=True)
def setup_listener(mapper, class_):
  '''
  Sets the database up so that User objects can have either a
  Vendor or a Customer associated with them, as an `account`.
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

