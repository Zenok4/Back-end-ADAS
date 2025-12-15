from database import db
from datetime import datetime


class DrowsinessEvents(db.Model):
    __tablename__ = "drowsiness_events"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    detection_event_id = db.Column(
        db.BigInteger,
        db.ForeignKey("detection_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    is_drowsy = db.Column(
        db.Boolean,
        nullable=False
    )

    eye_aspect_ratio = db.Column(
        db.Numeric(6, 4),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now
    )

    detection_event = db.relationship(
        "DetectionEvent",
        backref=db.backref("drowsy_events", lazy="dynamic")
    )
