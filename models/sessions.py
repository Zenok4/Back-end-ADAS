from database import db
from datetime import datetime

class UserSession(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    token_hash = db.Column(db.String(64), unique=True, nullable=False)

    user_agent_hash = db.Column(db.String(64), nullable=False)

    issued_at = db.Column(db.DateTime, default=datetime.now())
    expires_at = db.Column(db.DateTime, nullable=True)

    revoked = db.Column(db.Boolean, default=False)

    last_refresh_at = db.Column(db.DateTime)
    refresh_count = db.Column(db.Integer, default=0)

    
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    user = db.relationship("User", backref=db.backref("sessions", passive_deletes=True))

    def is_active(self):
        """Kiểm tra session còn hiệu lực không"""
        return not self.revoked and (self.expires_at is None or self.expires_at > datetime.now())