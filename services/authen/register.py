from werkzeug.security import generate_password_hash
from models.user import User
from database import db
from services.authen.otp_service import OTPService


class RegisterService:

    @staticmethod
    def register_with_username(username: str, password: str):
        """
        Đăng ký bằng username + password
        """
        existing = User.query.filter_by(username=username).first()
        if existing:
            return {"error": "Username already exists"}

        user = User(
            username=username,
            display_name=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User created", "user": user.to_dict()}

    @staticmethod
    def register_with_email(email: str, password: str, otp_code: str):
        """
        Đăng ký bằng email + password + OTP (purpose=verify)
        """
        existing = User.query.filter_by(email=email).first()
        if existing:
            return {"error": "Email already exists"}

        # Verify OTP trước
        otp_result = OTPService.verify_email_otp(email, password, otp_code, purpose="verify")
        if isinstance(otp_result, dict) and "error" in otp_result:
            return otp_result

        # Cắt display_name từ email
        local_part = email.split("@")[0]
        display_name = local_part.split(".")[0] if "." in local_part else local_part

        user = User(
            email=email,
            display_name=display_name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created", "user": user.to_dict()}

    @staticmethod
    def register_with_phone(phone: str, otp_code: str):
        """
        Đăng ký bằng phone + OTP
        """
        existing = User.query.filter_by(phone=phone).first()
        if existing:
            return {"error": "Phone already exists"}

        # Verify OTP trước
        otp_result = OTPService.verify_phone_otp(phone, otp_code, purpose="verify")
        if isinstance(otp_result, dict) and "error" in otp_result:
            return otp_result

        user = User(phone=phone)
        db.session.add(user)
        db.session.commit()

        # Sau khi có id thì mới update display_name
        user.display_name = f"user{user.id}"
        db.session.commit()

        return {"message": "User created", "user": user.to_dict()}
