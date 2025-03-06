from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from extensions import db, login

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class ClientNumber(db.Model):
    __tablename__ = 'client_numbers'
    number = db.Column(db.String(20), primary_key=True)
    mobile_carrier = db.Column(db.String(64), db.ForeignKey('mobile_carriers.name'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    mobile_carrier = db.Column(db.String(64), db.ForeignKey('mobile_carriers.name'))

    def modify(self, description):
        self.description = description

class CarrierName(Enum):
    ORANGE = 'Orange'
    MAROC_TELECOM = 'Maroc Telecom'
    INWI = 'Inwi'

class ProfitPercentage(Enum):
    ORANGE = 0.7
    MAROC_TELECOM = 0.4
    INWI = 0.5

class MobileCarrier(db.Model):
    __tablename__ = 'mobile_carriers'
    name = db.Column(db.Enum(CarrierName), primary_key=True)
    profit_percentage = db.Column(db.Enum(ProfitPercentage))