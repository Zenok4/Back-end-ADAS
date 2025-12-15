import smtplib
import os
import random
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from database import db
from models.auth_otp import AuthOTP
from models.user import User
from werkzeug.security import check_password_hash

class OTPService:

    # =======================================================
    #              INTERNAL SENDERS (Gửi thực tế)
    # =======================================================
    @staticmethod
    def _send_sms(phone, otp_code):
        """
        Tích hợp SMS API (VD: Twilio, eSMS, SpeedSMS).
        Hiện tại dùng Mock print để test luồng.
        """
        print(f"\n>>>> [SMS MOCK] Gửi tới {phone}: Mã OTP là {otp_code} <<<<\n")
        return True

    @staticmethod
    def _send_email(email, otp_code):
        """
        Gửi Email thực tế qua Google SMTP
        """
        sender_email = os.getenv("MAIL_USERNAME")  # Cấu hình trong .env
        sender_password = os.getenv("MAIL_PASSWORD") # App Password
        
        subject = "[ADAS] Mã xác thực của bạn"
        body = f"Mã xác thực (OTP) của bạn là: {otp_code}\nMã này có hiệu lực trong 5 phút.\n\nTrân trọng,\nĐội ngũ ADAS."

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = email

        try:
            # Kết nối tới Gmail SMTP
            # Nếu bạn dùng mail khác (Outlook/Zoho), hãy đổi host/port
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender_email, sender_password)
                smtp_server.sendmail(sender_email, email, msg.as_string())
            print(f"[EMAIL] Sent OTP to {email}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Không gửi được mail: {e}")
            return False

    # =======================================================
    #              CORE LOGIC (Sinh, Lưu & Kiểm tra)
    # =======================================================
    @staticmethod
    def create_and_send_otp(identifier, type_id, purpose="login"):
        """
        Hàm chung để sinh và gửi OTP.
        identifier: Email hoặc SĐT
        type_id: 'email' hoặc 'phone'
        purpose: 'login', 'register', 'reset'
        """
        otp_code = str(random.randint(100000, 999999))
        
        new_otp = AuthOTP(
            otp_code=otp_code,
            purpose=purpose,
            expires_at=datetime.now() + timedelta(minutes=5),
            used=False
        )
        
        if type_id == "email":
            new_otp.email = identifier
            OTPService._send_email(identifier, otp_code)
        else:
            new_otp.phone = identifier
            OTPService._send_sms(identifier, otp_code)
            
        db.session.add(new_otp)
        db.session.commit()
        return otp_code

    @staticmethod
    def validate_otp_only(identifier, otp_code, purpose):
        """
        Chỉ kiểm tra mã OTP có đúng và còn hạn không.
        KHÔNG kiểm tra mật khẩu hay user tồn tại.
        Dùng cho: Register, Verify Step 1, Forgot Password Step 2.
        """
        query = AuthOTP.query.filter_by(otp_code=otp_code, used=False, purpose=purpose)
        
        if "@" in identifier:
            query = query.filter_by(email=identifier)
        else:
            query = query.filter_by(phone=identifier)
            
        otp = query.first()

        if not otp:
            return {"valid": False, "error": "Mã OTP không đúng hoặc đã được sử dụng"}
        
        if otp.expires_at < datetime.now():
            return {"valid": False, "error": "Mã OTP đã hết hạn"}

        # Đánh dấu đã dùng ngay lập tức để tránh replay attack
        otp.used = True
        db.session.commit()
        return {"valid": True}

    # =======================================================
    #              LOGIN / VERIFY FLOWS
    # =======================================================
    @staticmethod
    def send_phone_otp(phone: str, purpose="login"):
        # Với mục đích login, user phải tồn tại mới gửi
        if purpose == "login":
            user = User.query.filter_by(phone=phone).first()
            if not user:
                return {"error": "User not found"}

        OTPService.create_and_send_otp(phone, "phone", purpose)
        return {"message": "OTP sent"}

    @staticmethod
    def verify_phone_otp(phone: str, otp_code: str, purpose="verify"):
        """Verify OTP và trả về User object (Dùng cho login)"""
        check = OTPService.validate_otp_only(phone, otp_code, purpose)
        if not check["valid"]:
            return {"error": check["error"]}

        user = User.query.filter_by(phone=phone).first()
        return user

    @staticmethod
    def send_email_otp(email: str, purpose="login"):
        if purpose == "login":
            user = User.query.filter_by(email=email).first()
            if not user:
                return {"error": "User not found"}

        OTPService.create_and_send_otp(email, "email", purpose)
        return {"message": "OTP sent"}

    @staticmethod
    def verify_email_otp(email: str, password: str, otp_code: str = None, purpose="verify"):
        """
        Dùng cho LOGIN Email: Check cả Password + OTP (nếu cần)
        """
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid email or password"}

        if otp_code:
            check = OTPService.validate_otp_only(email, otp_code, purpose)
            if not check["valid"]:
                return {"error": check["error"]}

        return user

    # =======================================================
    #            FORGOT PASSWORD SUPPORT
    # =======================================================
    @staticmethod
    def send_forgot_password_otp(identifier: str):
        type_id = "email" if "@" in identifier else "phone"
        
        # Check user tồn tại
        if type_id == "email":
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(phone=identifier).first()
            
        if not user:
            return {"error": "User not found"}

        # Dùng purpose='reset' để khớp với Enum trong Model
        OTPService.create_and_send_otp(identifier, type_id, purpose="reset")
        return {"message": "OTP sent"}

    @staticmethod
    def verify_forgot_password_otp(identifier: str, otp_code: str):
        """
        Xác thực OTP cho quên mật khẩu. Trả về User object để reset password.
        """
        check = OTPService.validate_otp_only(identifier, otp_code, purpose="reset")
        
        if not check["valid"]:
            return {"error": check["error"]}

        if "@" in identifier:
            return User.query.filter_by(email=identifier).first()
        else:
            return User.query.filter_by(phone=identifier).first()