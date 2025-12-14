from database import db
from datetime import datetime

class TripHistory(db.Model):
    __tablename__ = "trip_history"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    car_id = db.Column(
        db.BigInteger,
        db.ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=False
    )

    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)

    captured_at = db.Column(db.DateTime, nullable=False)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    user = db.relationship("User", backref="trip_history")
    car = db.relationship("Car", backref="trip_history")

    __table_args__ = (
        db.CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="check_trip_history_latitude"
        ),
        db.CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="check_trip_history_longitude"
        ),
        db.Index("idx_trip_history_car_time", "car_id", "captured_at"),
        db.Index("idx_trip_history_user_time", "user_id", "captured_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "car_id": self.car_id,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
