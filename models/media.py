from database import db
from datetime import datetime

class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    url = db.Column(db.String(1000), nullable=False)
    type = db.Column(db.Enum('image', 'video'), default='image')
    size_bytes = db.Column(db.BigInteger, nullable=True)
    checksum = db.Column(db.String(64), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())