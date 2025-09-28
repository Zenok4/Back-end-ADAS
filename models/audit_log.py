from database import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    object_type = db.Column(db.String(100), nullable=False)
    object_id = db.Column(db.String(100), nullable=False)
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    meta_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="audit_logs")