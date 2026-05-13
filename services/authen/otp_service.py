import smtplib
import os
import random
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

from database import db
from models.user import User
from werkzeug.security import check_password_hash
from redis_client import redis_client
from config import REDIS_OTP_TTL

load_dotenv()

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# Key pattern: otp:{purpose}:{identifier}
def _otp_key(identifier: str, purpose: str) -> str:
    return f"otp:{purpose}:{identifier}"


class OTPService:

    @staticmethod
    def _send_sms(phone, otp_code):
        print(f"\n>>>> [SMS MOCK] Gửi tới {phone}: Mã OTP là {otp_code} <<<<\n")
        return True

    @staticmethod
    def _send_email(email_to, otp_code):
        """Gửi email OTP qua Gmail SMTP."""
        if not MAIL_USERNAME or not MAIL_PASSWORD:
            print(">>>> [EMAIL ERROR] Thiếu MAIL_USERNAME hoặc MAIL_PASSWORD trong file .env")
            return False

        try:
            subject = "[ADAS] Mã xác thực OTP của bạn"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #333;">Xin chào,</h2>
                <p>Bạn vừa yêu cầu mã xác thực (OTP) từ hệ thống ADAS.</p>
                <p>Mã của bạn là: <strong style="font-size: 24px; color: #007bff; letter-spacing: 2px;">{otp_code}</strong></p>
                <p>Mã này có hiệu lực trong vòng 5 phút.</p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #777;">Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.</p>
            </body>
            </html>
            """

            msg = MIMEMultipart()
            msg['From'] = f"ADAS System <{MAIL_USERNAME}>"
            msg['To'] = email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, email_to, msg.as_string())
            server.quit()

            print(f">>>> [EMAIL SENT] Đã gửi OTP thành công tới {email_to}")
            return True

        except Exception as e:
            print(f">>>> [EMAIL ERROR] Lỗi gửi mail: {str(e)}")
            return False

    @staticmethod
    def create_and_send_otp(identifier: str, type_id: str, purpose: str = "login") -> str:
        """
        Tạo OTP, lưu vào Redis với TTL, rồi gửi đi.
        Key: otp:{purpose}:{identifier}
        Value: JSON {"code": "123456", "used": false}
        """
        otp_code = str(random.randint(100000, 999999))
        key = _otp_key(identifier, purpose)

        payload = json.dumps({"code": otp_code, "used": False})
        redis_client.set(key, payload, ex=REDIS_OTP_TTL)

        if type_id == "email":
            OTPService._send_email(identifier, otp_code)
        else:
            OTPService._send_sms(identifier, otp_code)

        return otp_code

    @staticmethod
    def validate_otp_only(identifier: str, otp_code: str, purpose: str) -> dict:
        """
        Kiểm tra OTP từ Redis.
        - Trả về {"valid": True} nếu đúng và chưa dùng
        - Xóa key sau khi dùng (one-time use)
        """
        key = _otp_key(identifier, purpose)
        raw = redis_client.get(key)

        if not raw:
            return {"valid": False, "error": "Mã OTP không đúng hoặc đã hết hạn"}

        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return {"valid": False, "error": "Dữ liệu OTP không hợp lệ"}

        if data.get("used"):
            return {"valid": False, "error": "Mã OTP đã được sử dụng"}

        if data.get("code") != otp_code:
            return {"valid": False, "error": "Mã OTP không đúng hoặc sai mục đích"}

        # Đánh dấu đã dùng và xóa key
        redis_client.delete(key)

        return {"valid": True}

    # ================= WRAPPER FUNCTIONS =================
    @staticmethod
    def send_phone_otp(phone: str, purpose: str = "login"):
        if purpose in ["login", "reset"]:
            user = User.query.filter_by(phone=phone).first()
            if not user:
                return {"error": "Số điện thoại chưa đăng ký"}
        OTPService.create_and_send_otp(phone, "phone", purpose)
        return {"message": "Đã gửi OTP"}

    @staticmethod
    def verify_phone_otp(phone: str, otp_code: str, purpose: str = "verify"):
        check = OTPService.validate_otp_only(phone, otp_code, purpose)
        if not check["valid"]:
            return {"error": check["error"]}
        user = User.query.filter_by(phone=phone).first()
        return user if user else {"success": True}

    @staticmethod
    def send_email_otp(email: str, purpose: str = "login"):
        if purpose in ["login", "reset"]:
            user = User.query.filter_by(email=email).first()
            if not user:
                return {"error": "Email chưa đăng ký"}
        OTPService.create_and_send_otp(email, "email", purpose)
        return {"message": "Đã gửi OTP"}

    @staticmethod
    def verify_email_otp(email: str, password: str = None, otp_code: str = None, purpose: str = "verify"):
        user = User.query.filter_by(email=email).first()
        if password:
            if not user or not check_password_hash(user.password_hash, password):
                return {"error": "Email hoặc mật khẩu không đúng"}
        if otp_code:
            check = OTPService.validate_otp_only(email, otp_code, purpose)
            if not check["valid"]:
                return {"error": check["error"]}
        return user if user else {"success": True}
