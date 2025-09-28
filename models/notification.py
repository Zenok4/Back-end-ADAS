from database import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    detection_event_id = db.Column(db.BigInteger, db.ForeignKey("detection_events.id", ondelete="SET NULL"), nullable=True)
    channel = db.Column(db.Enum('in_app', 'push', 'email', 'sms'), default='in_app')
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref="notifications")
    detection_event = db.relationship("DetectionEvent", backref="notifications")