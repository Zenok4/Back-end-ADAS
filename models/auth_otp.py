from database import db
from datetime import datetime

class AuthOTP(db.Model):
    __tablename__ = "auth_otps"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(30), nullable=False)
    otp_code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.Enum('login', 'verify', 'reset'), default='login')
    created_at = db.Column(db.DateTime, default=datetime.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
