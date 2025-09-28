from database import db
from datetime import datetime

class SignDetection(db.Model):
    __tablename__ = "sign_detections"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    detection_event_id = db.Column(db.BigInteger, db.ForeignKey("detection_events.id", ondelete="CASCADE"), nullable=False)
    sign_type = db.Column(db.String(100))
    confidence = db.Column(db.Numeric(5, 4))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    detection_event = db.relationship("DetectionEvent", backref="sign_detections")

    __table_args__ = (
        db.CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence'),
    )