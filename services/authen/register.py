from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from database import db
from services.authen.otp_service import OTPService
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

class RegisterService:

    # ================= QUAN TRỌNG: HÀM MỚI THÊM VÀO =================
    @staticmethod
    def send_otp_for_register(email: str):
        """
        Gửi OTP để đăng ký tài khoản mới.
        Điều kiện: Email CHƯA tồn tại trong hệ thống.
        """
        # 1. Kiểm tra Email đã tồn tại chưa
        existing = User.query.filter_by(email=email).first()
        if existing:
            return response_error(message="Email này đã được sử dụng. Vui lòng đăng nhập.", code=HttpCode.conflict)

        # 2. Gửi OTP với purpose='register'
        # (Đảm bảo DB cột purpose đã có giá trị 'register')
        OTPService.create_and_send_otp(email, "email", purpose="register")
        
        return response_success(message="Mã OTP đã được gửi tới email của bạn.", code=HttpCode.success)
    # ================================================================

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
        # 1. Validate OTP (purpose="register")
        # Lưu ý: Frontend đang gọi Register nên purpose phải là 'register' để khớp với lúc gửi
        check = OTPService.validate_otp_only(email, otp_code, purpose="register") 
        if not check["valid"]:
            return response_error(message=check.get("error", "Invalid OTP"), code=HttpCode.bad_request)

        # 2. Check Email tồn tại (Check lại lần nữa cho chắc)
        existing = User.query.filter_by(email=email).first()
        if existing:
            return response_error(message="Email already exists", code=HttpCode.conflict)

        local_part = email.split("@")[0]
        user_name = local_part.split(".")[0] if "." in local_part else local_part
        display_name = local_part.split(".")[0] if "." in local_part else local_part

        user = User(
            email=email,
            user_name=user_name,
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
    def register_with_phone(phone: str, password: str, otp_code: str):
        # (Logic giữ nguyên hoặc xóa nếu bạn đã bỏ đăng ký bằng phone ở Frontend)
        check = OTPService.validate_otp_only(phone, otp_code, purpose="register")
        if not check["valid"]:
            return response_error(message=check.get("error", "Invalid OTP"), code=HttpCode.bad_request)

        existing = User.query.filter_by(phone=phone).first()
        if existing:
            return response_error(message="Phone already exists", code=HttpCode.conflict)

        user = User(
            phone=phone,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(user)
            db.session.commit()
            
            user.display_name = f"user{user.id}"
            db.session.commit()

            return response_success(data=user.to_dict(), key="user", message="User created", code=HttpCode.created)
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(message=f"Database error: {str(e)}", code=HttpCode.internal_server_error)