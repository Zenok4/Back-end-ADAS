from database import db, get_db_url
from models import user, auth_otp, sessions
from flask import Flask

def init_dtb(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_db_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)