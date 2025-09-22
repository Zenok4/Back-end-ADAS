from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from database import db
from services.authen.otp_service import OTPService
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode


class RegisterService:

    @staticmethod
    def register_with_username(username: str, password: str):
        existing = User.query.filter_by(username=username).first()
        if existing:
            return response_error(message="Username already exists", code=HttpCode.conflict)

        user = User(
            username=username,
            display_name=username,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(user)
            db.session.commit()
            return response_success(data=user.to_dict(), key="user", message="User created", code=HttpCode.created)
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(message=f"Database error: {str(e)}", code=HttpCode.internal_server_error)

    @staticmethod
    def register_with_email(email: str, password: str, otp_code: str):
        existing = User.query.filter_by(email=email).first()
        if existing:
            return response_error(message="Email already exists", code=HttpCode.conflict)

        otp_result = OTPService.verify_email_otp(email, password, otp_code, purpose="verify")
        if not otp_result.get("success", False):
            return otp_result

        local_part = email.split("@")[0]
        display_name = local_part.split(".")[0] if "." in local_part else local_part

        user = User(
            email=email,
            display_name=display_name,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(user)
            db.session.commit()
            return response_success(data=user.to_dict(), key="user", message="User created", code=HttpCode.created)
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(message=f"Database error: {str(e)}", code=HttpCode.internal_server_error)

    @staticmethod
    def register_with_phone(phone: str, otp_code: str):
        existing = User.query.filter_by(phone=phone).first()
        if existing:
            return response_error(message="Phone already exists", code=HttpCode.conflict)

        otp_result = OTPService.verify_phone_otp(phone, otp_code, purpose="verify")
        if not otp_result.get("success", False):
            return otp_result

        user = User(phone=phone)
        try:
            db.session.add(user)
            db.session.commit()

            # update display_name sau khi có id
            user.display_name = f"user{user.id}"
            db.session.commit()

            return response_success(data=user.to_dict(), key="user", message="User created", code=HttpCode.created)
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(message=f"Database error: {str(e)}", code=HttpCode.internal_server_error)