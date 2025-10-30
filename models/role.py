from database import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    level = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    permissions = db.relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )

    users = db.relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )

    def to_dict(self, include_permissions=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_permissions:
            data["permissions"] = [p.to_dict() for p in self.permissions]
        return data
