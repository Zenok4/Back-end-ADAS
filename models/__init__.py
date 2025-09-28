from database import db, get_db_url
from models import user, auth_otp, sessions, permission, role, role_permission, user_role
from models import permission_group, media, detection_event, drowsiness_event  
from models import lane_event, object_detection, sign_detection, notification, audit_log  
from flask import Flask

def init_dtb(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_db_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)