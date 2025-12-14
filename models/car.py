from database import db
from datetime import datetime

class Car(db.Model):
    __tablename__ = "cars"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    plate_number = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255))

    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    user = db.relationship("User", backref="cars")

    __table_args__ = (
        db.UniqueConstraint("plate_number", name="uq_cars_plate_number"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plate_number": self.plate_number,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
