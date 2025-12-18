from datetime import datetime
from database import db
from sqlalchemy import event
from models.user_role import UserRole 

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255))
    
    # [SỬA] Thêm cột address
    address = db.Column(db.String(255), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    roles = db.relationship("Role", secondary="user_roles", back_populates="users")
    
    # Relationship với Car: Dùng backref="user" tại đây là đủ
    cars = db.relationship("Car", backref="user", lazy=True)

    def to_dict(self, include_roles=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "display_name": self.display_name,
            "address": self.address, 
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # [SỬA] Logic lấy thông tin xe để trả về Frontend
        if self.cars and len(self.cars) > 0:
            first_car = self.cars[0]
            # Key ở đây phải khớp với models/car.py vừa sửa
            data["vehicle_name"] = first_car.vehicle_name
            data["license_plate"] = first_car.license_plate
        else:
            data["vehicle_name"] = ""
            data["license_plate"] = ""

        if include_roles:
            data["roles"] = [r.to_dict() for r in self.roles]
        return data

@event.listens_for(User, 'after_insert')
def assign_default_role(mapper, connection, target):
    default_role_id = 1
    connection.execute(
        db.insert(UserRole.__table__).values(user_id=target.id, role_id=default_role_id)
    )