from database import db
from models import user, auth_otp
from flask import Flask

def init_app(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✅ Database schema initialized!")