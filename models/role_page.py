from database import db
from datetime import datetime

class RolePage(db.Model):
    __tablename__ = "role_pages"

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())