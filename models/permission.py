from database import db
from datetime import datetime

class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(100), unique=True, nullable=False)   
    title = db.Column(db.String(100), nullable=False)              
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())

    roles = db.relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }