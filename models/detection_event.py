from database import db
from datetime import datetime

class DetectionEvent(db.Model):
    __tablename__ = "detection_events"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = db.Column(db.Enum('drowsiness', 'lane_departure', 'object', 'sign'), nullable=False, index=True)
    severity = db.Column(db.Enum('info', 'warning', 'critical'), default='warning')
    event_time = db.Column(db.DateTime, nullable=False)
    media_id = db.Column(db.BigInteger, db.ForeignKey("media.id", ondelete="SET NULL"), nullable=True)
    payload = db.Column(db.JSON, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref="detection_events")
    media = db.relationship("Media", backref="detection_events")

    __table_args__ = (
        db.Index('idx_user_event', 'user_id', 'event_type'),
    )
