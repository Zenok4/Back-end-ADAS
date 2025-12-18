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

    # [SỬA] Đổi tên cột cho khớp với Frontend gửi xuống
    license_plate = db.Column(db.String(50), nullable=False) 
    vehicle_name = db.Column(db.String(255))                 

    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # [QUAN TRỌNG] Đã xóa dòng dưới đây để tránh lỗi "Multiple backref" 
    # vì bên models/user.py đã định nghĩa relationship rồi.
    # user = db.relationship("User", backref="cars") 

    __table_args__ = (
        # Đặt tên constraint rõ ràng để tránh lỗi khi migrate
        db.UniqueConstraint("license_plate", name="uq_cars_license_plate"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "license_plate": self.license_plate,
            "vehicle_name": self.vehicle_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }