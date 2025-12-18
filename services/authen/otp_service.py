import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv  # <--- Import thư viện đọc .env

from database import db
from models.auth_otp import AuthOTP
from models.user import User
from werkzeug.security import check_password_hash

# 1. Load nội dung file .env vào biến môi trường
load_dotenv()

# 2. Lấy cấu hình từ .env (Code sẽ tự tìm biến tương ứng trong file .env bạn gửi)
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # Lấy groupshytpm3@gmail.com
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # Lấy dqfi cjyp mdbe dhlb

class OTPService:

    @staticmethod
    def _send_sms(phone, otp_code):
        # Giả lập gửi SMS (in ra màn hình console)
        print(f"\n>>>> [SMS MOCK] Gửi tới {phone}: Mã OTP là {otp_code} <<<<\n")
        return True

    @staticmethod
    def _send_email(email_to, otp_code):
        """Hàm gửi email thực tế qua Gmail SMTP dùng thông tin từ .env"""
        
        # Kiểm tra xem đã cấu hình env chưa
        if not MAIL_USERNAME or not MAIL_PASSWORD:
            print(">>>> [EMAIL ERROR] Thiếu MAIL_USERNAME hoặc MAIL_PASSWORD trong file .env")
            return False

        try:
            # Tạo nội dung email
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

            # Kết nối tới Gmail
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            server.starttls() # Mã hóa kết nối
            
            # Đăng nhập (Mật khẩu app password có khoảng trắng vẫn chạy tốt)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            
            # Gửi mail
            server.sendmail(MAIL_USERNAME, email_to, msg.as_string())
            server.quit()
            
            print(f">>>> [EMAIL SENT] Đã gửi OTP thành công tới {email_to}")
            return True

        except Exception as e:
            print(f">>>> [EMAIL ERROR] Lỗi gửi mail: {str(e)}")
            return False

    @staticmethod
    def create_and_send_otp(identifier, type_id, purpose="login"):
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
        """Kiểm tra OTP, dùng chung cho mọi mục đích"""
        query = AuthOTP.query.filter_by(otp_code=otp_code, used=False, purpose=purpose)
        
        if "@" in identifier:
            query = query.filter_by(email=identifier)
        else:
            query = query.filter_by(phone=identifier)
            
        otp = query.first()

        if not otp:
            return {"valid": False, "error": "Mã OTP không đúng hoặc sai mục đích"}
        
        if otp.expires_at < datetime.now():
            return {"valid": False, "error": "Mã OTP đã hết hạn"}

        otp.used = True
        db.session.commit()
        return {"valid": True}

    # ================= WRAPPER FUNCTIONS (Giữ nguyên) =================
    @staticmethod
    def send_phone_otp(phone: str, purpose="login"):
        if purpose in ["login", "reset"]:
            user = User.query.filter_by(phone=phone).first()
            if not user: return {"error": "Số điện thoại chưa đăng ký"}
        OTPService.create_and_send_otp(phone, "phone", purpose)
        return {"message": "Đã gửi OTP"}

    @staticmethod
    def verify_phone_otp(phone: str, otp_code: str, purpose="verify"):
        check = OTPService.validate_otp_only(phone, otp_code, purpose)
        if not check["valid"]: return {"error": check["error"]}
        user = User.query.filter_by(phone=phone).first()
        return user if user else {"success": True}

    @staticmethod
    def send_email_otp(email: str, purpose="login"):
        if purpose in ["login", "reset"]:
            user = User.query.filter_by(email=email).first()
            if not user: return {"error": "Email chưa đăng ký"}
        OTPService.create_and_send_otp(email, "email", purpose)
        return {"message": "Đã gửi OTP"}

    @staticmethod
    def verify_email_otp(email: str, password: str = None, otp_code: str = None, purpose="verify"):
        user = User.query.filter_by(email=email).first()
        if password:
            if not user or not check_password_hash(user.password_hash, password):
                return {"error": "Email hoặc mật khẩu không đúng"}
        if otp_code:
            check = OTPService.validate_otp_only(email, otp_code, purpose)
            if not check["valid"]: return {"error": check["error"]}
        return user if user else {"success": True}