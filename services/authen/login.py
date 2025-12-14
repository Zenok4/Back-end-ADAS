from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from datetime import timedelta

import logger
from models.user import User
from services.authen.otp_service import OTPService
from services.authen.session_service import SessionService

import jwt
from config import REFRESH_SECRET_KEY

from database import db


class LoginService:

    @staticmethod
    def login_with_username(username, password, request):
        """
        Đăng nhập bằng username + password.
        - Trả về access_token + refresh_token + session_id + user nếu đúng
        """
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid username or password"}

        return LoginService._generate_token(user, request)

    @staticmethod
    def request_phone_otp(phone: str):
        """Gửi OTP cho user theo phone."""
        return OTPService.send_phone_otp(phone)

    @staticmethod
    def login_with_phone_otp(phone: str, otp_code: str):
        """
        Xác thực OTP và trả access_token + refresh_token + session nếu đúng.
        """
        user_or_error = OTPService.verify_otp(phone, otp_code)
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        return LoginService._generate_token(user_or_error)

    @staticmethod
    def request_email_otp(email: str):
        """Gửi OTP cho email."""
        return OTPService.send_email_otp(email)

    @staticmethod
    def login_with_email(email: str, password: str, otp_code: str = None):
        """
        Đăng nhập bằng email + password + OTP (nếu có).
        """
        user_or_error = OTPService.verify_email_otp(email, password, otp_code, "login")
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        return LoginService._generate_token(user_or_error)

    # ================== Internal helpers ==================

    @staticmethod
    def _generate_token(user, request):
        """
        Sinh access token + refresh token, lưu session với refresh_token hash.
        """
        access_expires = timedelta(minutes=15)
        refresh_expires = timedelta(days=7)

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=access_expires
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=refresh_expires
        )

        # lưu session
        session_id = SessionService.create_session(user.id, refresh_token, request=request)

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": access_expires.total_seconds(),
            "session_id": session_id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name,
            },
        }

    @staticmethod
    def refresh_access_token(session: str):
        """
        Tạo access token mới nếu session hợp lệ.

        Quy trình xử lý:
        1. Lấy user_id trực tiếp từ session trong DB
        2. Sinh access token mới với thời hạn cố định (mặc định: 15 phút)
        3. Trả về access token mới cho client
        """
        # Check trong DB
        if not session:
            return {"error": "Invalid session"}

        try:
            new_access_token = create_access_token(
                identity=str(session.user_id),
                expires_delta=timedelta(minutes=15)
            )

            return {
                "access_token": new_access_token,
                "expires_in": 15 * 60
            }

        except Exception as e:
            logger.exception(
                "Failed to refresh access token for session_id=%s",
                getattr(session, "session_id", None)
            )
            return {"error": "Internal server error"}

    @staticmethod
    def logout(session_id: str):
        """
        Đăng xuất: revoke session.
        """
        return SessionService.revoke_session(session_id)
    
    # ================== FORGOT PASSWORD - EMAIL ==================
    @staticmethod
    def request_forgot_password_email(email: str):
        """
        Gửi OTP phục hồi mật khẩu qua email.
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return {"error": "User not found"}

            return OTPService.send_email_otp(email, purpose="verify")

        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}

    @staticmethod
    def reset_password_email(email: str, otp_code: str, new_password: str):
        """
        Xác thực OTP và cập nhật mật khẩu mới qua email.
        """
        try:
            user_or_error = OTPService.verify_email_otp(email, otp_code=otp_code, purpose="verify")
            if isinstance(user_or_error, dict) and "error" in user_or_error:
                return user_or_error

            user = user_or_error
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return {"success": True, "message": "Password has been reset successfully."}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Internal server error: {str(e)}"}

    # ================== FORGOT PASSWORD - PHONE ==================
    @staticmethod
    def request_forgot_password_phone(phone: str):
        """
        Gửi OTP phục hồi mật khẩu qua số điện thoại.
        """
        try:
            user = User.query.filter_by(phone=phone).first()
            if not user:
                return {"error": "User not found"}

            return OTPService.send_phone_otp(phone, purpose="verify")

        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}

    @staticmethod
    def reset_password_phone(phone: str, otp_code: str, new_password: str):
        """
        Xác thực OTP và cập nhật mật khẩu mới qua phone.
        """
        try:
            user_or_error = OTPService.verify_phone_otp(phone, otp_code=otp_code, purpose="verify")
            if isinstance(user_or_error, dict) and "error" in user_or_error:
                return user_or_error

            user = user_or_error
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return {"success": True, "message": "Password has been reset successfully."}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Internal server error: {str(e)}"}
