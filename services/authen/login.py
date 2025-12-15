from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
import jwt

from models.user import User
from services.authen.otp_service import OTPService
from services.authen.session_service import SessionService
from config import REFRESH_SECRET_KEY
from database import db


class LoginService:

    # ================== LOGIN FLOW ==================

    @staticmethod
    def login_with_username(username, password):
        """
        Đăng nhập bằng username + password.
        """
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid username or password"}

        return LoginService._generate_token(user)

    @staticmethod
    def request_phone_otp(phone: str):
        """Gửi OTP đăng nhập cho user theo phone."""
        # Gọi hàm send_phone_otp (purpose='login' mặc định)
        return OTPService.send_phone_otp(phone)

    @staticmethod
    def login_with_phone_otp(phone: str, otp_code: str):
        """
        Xác thực OTP và trả token.
        """
        # SỬA: Gọi đúng hàm verify_phone_otp
        user_or_error = OTPService.verify_phone_otp(phone, otp_code, purpose="login")
        
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        return LoginService._generate_token(user_or_error)

    @staticmethod
    def request_email_otp(email: str):
        """Gửi OTP đăng nhập cho email."""
        return OTPService.send_email_otp(email)

    @staticmethod
    def login_with_email(email: str, password: str, otp_code: str = None):
        """
        Đăng nhập bằng email + password + OTP (nếu cấu hình yêu cầu).
        """
        # SỬA: Gọi đúng verify_email_otp (hàm này check pass + otp)
        user_or_error = OTPService.verify_email_otp(email, password, otp_code, purpose="login")
        
        if isinstance(user_or_error, dict) and "error" in user_or_error:
            return user_or_error

        return LoginService._generate_token(user_or_error)

    # ================== FORGOT PASSWORD FLOW ==================
    # (Sử dụng các hàm chuyên biệt từ OTPService mới)

    @staticmethod
    def request_forgot_password_email(email: str):
        """
        Gửi OTP phục hồi mật khẩu qua email.
        """
        # Gọi hàm chuyên biệt, nó tự handle check user tồn tại
        return OTPService.send_forgot_password_otp(email)

    @staticmethod
    def reset_password_email(email: str, otp_code: str, new_password: str):
        """
        Xác thực OTP và cập nhật mật khẩu mới qua email.
        """
        try:
            # 1. Verify OTP (Dùng hàm verify_forgot_password_otp để KHÔNG check pass cũ)
            user_or_error = OTPService.verify_forgot_password_otp(email, otp_code)
            
            if isinstance(user_or_error, dict) and "error" in user_or_error:
                return user_or_error

            # 2. Update Password
            user = user_or_error
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return {"success": True, "message": "Password has been reset successfully."}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Internal server error: {str(e)}"}

    @staticmethod
    def request_forgot_password_phone(phone: str):
        """
        Gửi OTP phục hồi mật khẩu qua số điện thoại.
        """
        return OTPService.send_forgot_password_otp(phone)

    @staticmethod
    def reset_password_phone(phone: str, otp_code: str, new_password: str):
        """
        Xác thực OTP và cập nhật mật khẩu mới qua phone.
        """
        try:
            # 1. Verify OTP
            user_or_error = OTPService.verify_forgot_password_otp(phone, otp_code)
            
            if isinstance(user_or_error, dict) and "error" in user_or_error:
                return user_or_error

            # 2. Update Password
            user = user_or_error
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return {"success": True, "message": "Password has been reset successfully."}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Internal server error: {str(e)}"}

    # ================== INTERNAL HELPERS ==================

    @staticmethod
    def _generate_token(user):
        """
        Sinh access token + refresh token, lưu session.
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
        if not SessionService.validate_session(refresh_token):
            return {"error": "Invalid or revoked refresh token"}

        try:
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("id") # Lưu ý: payload có thể khác tùy jwt implementation của bạn
            # Nếu identity là string (user_id), jwt-extended sẽ decode ra string 'sub'.
            # Nếu identity là dict, nó sẽ nằm trong 'sub'.
            # Đoạn này giữ nguyên theo code cũ của bạn nếu nó đang chạy đúng.
            
            # Giả sử identity là user_id (string)
            new_access_token = create_access_token(
                identity=payload.get("sub"), 
                expires_delta=timedelta(minutes=15)
            )
            return {"access_token": new_access_token}

        except jwt.ExpiredSignatureError:
            return {"error": "Refresh token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid refresh token"}

    @staticmethod
    def logout(session_id: str):
        return SessionService.revoke_session(session_id)