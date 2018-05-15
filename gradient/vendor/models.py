from config import Config
from ..datastore import db
from ..user import HasUser
from datetime import datetime
from sqlalchemy_utils import EncryptedType


class Vendor(db.Model, HasUser):
  id           = db.Column(db.Integer(), 
                           primary_key=True)
  created_at   = db.Column(db.DateTime(), 
                           default=datetime.utcnow)
  updated_at   = db.Column(db.DateTime(), 
                           default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
  slug         = db.Column(db.Unicode(), 
                           index=True, 
                           unique=True)
  company_name = db.Column(db.Unicode(255))
  stripe_sk    = db.Column(EncryptedType(db.String, 
                                         Config.SECRET_KEY))
  stripe_pk    = db.Column(EncryptedType(db.String, 
                                         Config.SECRET_KEY))
  redirect_url = db.Column(db.Unicode())

  def render_stripe_sk(self):
      return '****{}'.format(self.stripe_sk[-4:])

  def render_stripe_pk(self):
      return '****{}'.format(self.stripe_pk[-4:])
