from database import db
from datetime import datetime, timezone

class UserSession(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Lưu refresh token dưới dạng hash (SHA256)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)

    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    revoked = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    create_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Quan hệ tới User (nếu cần lấy user từ session)
    user = db.relationship("User", backref="sessions")

    def is_active(self):
        """Kiểm tra session còn hiệu lực không"""
        return not self.revoked and (self.expires_at is None or self.expires_at > datetime.now(timezone.utc))
