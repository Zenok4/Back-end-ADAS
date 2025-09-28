from database import db
from datetime import datetime

class ObjectDetection(db.Model):
    __tablename__ = "object_detections"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    detection_event_id = db.Column(db.BigInteger, db.ForeignKey("detection_events.id", ondelete="CASCADE"), nullable=False)
    object_type = db.Column(db.String(100))
    bbox = db.Column(db.JSON)
    confidence = db.Column(db.Numeric(5, 4))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    detection_event = db.relationship("DetectionEvent", backref="object_detections")

    __table_args__ = (
        db.CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_objects_confidence'),
    )