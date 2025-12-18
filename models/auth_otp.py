from database import db
from datetime import datetime

class AuthOTP(db.Model):
    __tablename__ = "auth_otps"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    otp_code = db.Column(db.String(10), nullable=False)
    
    # === SỬA TẠI ĐÂY: Thêm 'change_password' vào Enum ===
    purpose = db.Column(db.Enum('login', 'register', 'verify', 'reset', 'change_password'), default='login') 
    
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.CheckConstraint('expires_at > created_at', name='check_expires_at'),
    )