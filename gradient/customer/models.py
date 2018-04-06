from ..datastore import db
from ..user import HasUser
from ..util import FormEnum


class MaritalStatus(FormEnum):
    NOT_MARRIED = 0
    MARRIED = 1


class Customer(db.Model, HasUser):
    id                   = db.Column(db.Integer(), primary_key=True)
    individual_income    = db.Column(db.Integer()) # in cents
    household_income     = db.Column(db.Integer()) # in cents
    marital_status       = db.Column(db.Enum(MaritalStatus), 
                                     default=MaritalStatus.NOT_MARRIED, 
                                     nullable=False)
    dependents           = db.Column(db.Integer(), default=0)
    signature            = db.Column(db.String())
    stripe_id            = db.Column(db.String(255))


