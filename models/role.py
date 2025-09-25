from database import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    permissions = db.relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )

    def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            }