from database import db
from datetime import datetime

class LaneEvent(db.Model):
    __tablename__ = "lane_events"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    detection_event_id = db.Column(db.BigInteger, db.ForeignKey("detection_events.id", ondelete="CASCADE"), nullable=False)
    confidence = db.Column(db.Numeric(5, 4))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    detection_event = db.relationship("DetectionEvent", backref="lane_events")

    __table_args__ = (
        db.CheckConstraint('deviation_meters >= 0', name='check_deviation_meters'),
        db.CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_lane_confidence'),
    )