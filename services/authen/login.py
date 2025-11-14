from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from datetime import timedelta

from models.user import User
from services.authen.otp_service import OTPService
from services.authen.session_service import SessionService

import jwt
from config import REFRESH_SECRET_KEY

from database import db


class LoginService:

    @staticmethod
    def login_with_username(username, password):
        """
        Đăng nhập bằng username + password.
        - Trả về access_token + refresh_token + session_id + user nếu đúng
        """
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid username or password"}

        return LoginService._generate_token(user)

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
    def _generate_token(user):
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
        session_id = SessionService.create_session(user.id, refresh_token)

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
    def refresh_access_token(refresh_token: str):
        """
        Tạo access token mới nếu refresh_token hợp lệ.
        """
        # Check trong DB
        if not SessionService.validate_session(refresh_token):
            return {"error": "Invalid or revoked refresh token"}

        try:
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("id")
            username = payload.get("username")

            new_access_token = create_access_token(
                identity={"id": user_id, "username": username},
                expires_delta=timedelta(minutes=15)
            )

            return {"access_token": new_access_token}

        except jwt.ExpiredSignatureError:
            return {"error": "Refresh token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid refresh token"}

    @staticmethod
    def logout(session_id: str):
        """
        Đăng xuất: revoke session.
        """
        return SessionService.revoke_session(session_id)
    
    # ================== FORGOT PASSWORD FLOW ==================

    @staticmethod
    def request_forgot_password(identifier: str):
        """
        Gửi OTP phục hồi mật khẩu qua email hoặc phone.
        - identifier có thể là email hoặc phone
        """
        user = User.query.filter(
            (User.email == identifier) | (User.phone == identifier)
        ).first()

        if not user:
            return {"error": "User not found"}

        
        return OTPService.send_forgot_password_otp(identifier)

    @staticmethod
    def reset_password(identifier: str, otp_code: str, new_password: str):
        """
        Xác thực OTP và cập nhật mật khẩu mới.
        identifier: email hoặc phone
        """
        # 1) Verify OTP
        user_or_error = OTPService.verify_forgot_password_otp(identifier, otp_code)
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        user = user_or_error

        # 2) Update password
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(new_password)

        db.session.commit()

        return {
            "success": True,
            "message": "Password has been reset successfully."
        }
