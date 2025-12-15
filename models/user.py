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
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # === SỬA TẠI ĐÂY: Bỏ dấu ngoặc () sau datetime.now ===
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    roles = db.relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )

    def to_dict(self, include_roles=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_roles:
            data["roles"] = [r.to_dict() for r in self.roles]
        return data