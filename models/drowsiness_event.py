from database import db
from datetime import datetime

class DrowsinessEvent(db.Model):
    __tablename__ = "drowsiness_events"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    detection_event_id = db.Column(db.BigInteger, db.ForeignKey("detection_events.id", ondelete="CASCADE"), nullable=False)
    eye_closure_duration_ms = db.Column(db.Integer)
    yawn_detected = db.Column(db.Boolean, default=False)
    head_nod_count = db.Column(db.Integer, default=0)
    confidence = db.Column(db.Numeric(5, 4))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    detection_event = db.relationship("DetectionEvent", backref="drowsiness_events")

    __table_args__ = (
        db.CheckConstraint('eye_closure_duration_ms >= 0', name='check_eye_closure_duration_ms'),
        db.CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence'),
    )