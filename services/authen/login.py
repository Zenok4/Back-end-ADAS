from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from datetime import datetime
from models.user import User
from models.auth_otp import AuthOTP
from database import db
from services.authen.otp_service import OTPService

class LoginService:

    @staticmethod
    def login_with_username(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid username or password"}
        return LoginService._generate_token(user)

    @staticmethod
    def request_phone_otp(phone: str):
        """
        Service gửi OTP cho user theo phone
        """
        return OTPService.send_otp(phone)

    @staticmethod
    def login_with_phone_otp(phone: str, otp_code: str):
        """
        Service xác thực OTP và trả token nếu đúng
        """
        user_or_error = OTPService.verify_otp(phone, otp_code)
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        user = user_or_error
        token = LoginService._generate_token(user)
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name
            }
        }

    @staticmethod
    def request_email_otp(email: str):
        """
        Service gửi OTP cho email
        """
        return OTPService.send_email_otp(email)

    @staticmethod
    def login_with_email(email: str, password: str, otp_code: str = None):
        """
        Service login bằng email + password + OTP (nếu có)
        """
        user_or_error = OTPService.verify_email_otp(email, password, otp_code)
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        user = user_or_error
        token = LoginService._generate_token(user)
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name
            }
        }

    @staticmethod
    def _generate_token(user):
        token = create_access_token(identity={"id": user.id, "username": user.username})
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name
            }
        }
