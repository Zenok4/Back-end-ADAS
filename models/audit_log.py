from database import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    object_type = db.Column(db.String(100))
    object_id = db.Column(db.String(100))
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref="audit_logs")