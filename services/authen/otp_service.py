from datetime import datetime, timedelta, timezone
from models.auth_otp import AuthOTP
from models.user import User
from database import db
import random
from werkzeug.security import check_password_hash

class OTPService:

    @staticmethod
    def send_phone_otp(phone: str, purpose="login"):
        """
        Kiểm tra user tồn tại, tạo OTP, lưu DB và trả OTP (hoặc gửi qua SMS)
        """
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return {"error": "User not found"}

        otp_code = str(random.randint(100000, 999999))
        otp = AuthOTP(
            phone=phone,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        db.session.add(otp)
        db.session.commit()

        # Gửi OTP qua SMS/Email
        OTPService._send_sms(phone, otp_code)
        return {"message": "OTP sent"}

    @staticmethod
    def verify_phone_otp(phone: str, otp_code: str, purpose="verify"):
        """
        Kiểm tra OTP hợp lệ, đánh dấu đã dùng, trả user nếu đúng
        """
        otp = AuthOTP.query.filter_by(phone=phone, otp_code=otp_code, used=False, purpose=purpose).first()
        if not otp:
            return {"error": "OTP not found or already used"}
        if otp.expires_at < datetime.now(timezone.utc):
            return {"error": "OTP expired"}

        user = User.query.filter_by(phone=phone).first()
        if not user:
            return {"error": "User not found"}

        otp.used = True
        db.session.commit()
        return user

    @staticmethod
    def _send_sms(phone, otp_code):
        # gọi API SMS thực tế, ví dụ Twilio
        print(f"Send OTP {otp_code} to {phone}")


    ### ================== Email ==================
    @staticmethod
    def send_email_otp(email: str, purpose="login"):
        """
        Kiểm tra user tồn tại theo email, tạo OTP, lưu DB và gửi email
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"error": "User not found"}

        otp_code = str(random.randint(100000, 999999))
        otp = AuthOTP(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        db.session.add(otp)
        db.session.commit()

        OTPService._send_email(email, otp_code)
        return {"message": "OTP sent"}

    @staticmethod
    def verify_email_otp(email: str, password: str, otp_code: str = None, purpose="verify"):
        """
        Kiểm tra email + password + OTP (nếu có)
        """
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid email or password"}

        if otp_code:
            otp = AuthOTP.query.filter_by(otp_code=otp_code, email=email, used=False, purpose=purpose).first()
            if not otp or otp.expires_at < datetime.now(timezone.utc):
                return {"error": "Invalid or expired verification code"}
            otp.used = True
            db.session.commit()

        return user

    @staticmethod
    def _send_email(email, otp_code):
        # thực tế sẽ gửi email qua API SMTP / SendGrid / etc
        print(f"Send OTP {otp_code} to email {email}")
