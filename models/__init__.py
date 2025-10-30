from database import db, get_db_url
from flask import Flask

from models import user_role, role_permission

from models import user, role, permission

from models import auth_otp, sessions, media, detection_event, drowsiness_event  
from models import lane_event, object_detection, sign_detection, notification, audit_log  


def init_dtb(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_db_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
