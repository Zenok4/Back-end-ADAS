from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from database import db
from services.authen.otp_service import OTPService
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

class RegisterService:

    @staticmethod
    def send_otp_for_register(email: str):
        """
        Gửi OTP để đăng ký tài khoản mới.
        """
        existing = User.query.filter_by(email=email).first()
        if existing:
            return response_error(message="Email này đã được sử dụng. Vui lòng đăng nhập.", code=HttpCode.conflict)

        # Gửi OTP với purpose='register'
        OTPService.create_and_send_otp(email, "email", purpose="register")
        
        return response_success(message="Mã OTP đã được gửi tới email của bạn.", code=HttpCode.success)

    @staticmethod
    def register_with_username(username: str, password: str):
        existing = User.query.filter_by(username=username).first()
        if existing:
            return response_error(message="Tên đăng nhập đã tồn tại", code=HttpCode.conflict)

        user = User(
            username=username,
            display_name=username,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(user)
            db.session.commit()
            return response_success(data=user.to_dict(), key="user", message="Đăng ký thành công", code=HttpCode.created)
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(message=f"Lỗi cơ sở dữ liệu: {str(e)}", code=HttpCode.internal_server_error)

    @staticmethod
    def register_with_email(email: str, password: str, otp_code: str):
        # 1. Validate OTP
        check = OTPService.validate_otp_only(email, otp_code, purpose="register") 
        if not check["valid"]:
            return response_error(message=check.get("error", "Mã OTP không hợp lệ"), code=HttpCode.bad_request)

        # 2. Check Email tồn tại
        existing = User.query.filter_by(email=email).first()
        if existing:
            return response_error(message="Email đã tồn tại", code=HttpCode.conflict)

        # Tạo username từ email (lấy phần trước @)
        local_part = email.split("@")[0]
        # Xử lý tên hiển thị
        display_name = local_part.split(".")[0] if "." in local_part else local_part

        # [QUAN TRỌNG] Sửa user_name thành username ở dòng dưới đây
        user = User(
            email=email,
            username=local_part,  # <--- ĐÃ SỬA: Dùng 'username' cho đúng Model
            display_name=display_name,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(user)
            db.session.commit()
            return response_success(data=user.to_dict(), key="user", message="Đăng ký thành công", code=HttpCode.created)
        
        except SQLAlchemyError as e:
            db.session.rollback()
            # Xử lý trường hợp username (tự sinh) bị trùng
            if "Duplicate entry" in str(e) and "users.username" in str(e):
                # Nếu trùng username tự sinh, thử thêm số ngẫu nhiên vào sau
                import random
                try:
                    user.username = f"{local_part}{random.randint(100, 999)}"
                    db.session.add(user)
                    db.session.commit()
                    return response_success(data=user.to_dict(), key="user", message="Đăng ký thành công", code=HttpCode.created)
                except Exception:
                    pass
                return response_error(message="Tên người dùng tự sinh từ email đã tồn tại. Vui lòng thử email khác.", code=HttpCode.conflict)
            
            return response_error(message=f"Lỗi hệ thống: {str(e)}", code=HttpCode.internal_server_error)

    @staticmethod
    def register_with_phone(phone: str, password: str, otp_code: str):
        check = OTPService.validate_otp_only(phone, otp_code, purpose="register")
        if not check["valid"]:
            return response_error(message=check.get("error", "Invalid OTP"), code=HttpCode.bad_request)

        existing = User.query.filter_by(phone=phone).first()
        if existing:
            return response_error(message="Số điện thoại đã tồn tại", code=HttpCode.conflict)

        user = User(
            phone=phone,
            username=phone, # Dùng số điện thoại làm username
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(user)
            db.session.commit()
            
            user.display_name = f"user{user.id}"
            db.session.commit()

            return response_success(data=user.to_dict(), key="user", message="Đăng ký thành công", code=HttpCode.created)
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(message=f"Database error: {str(e)}", code=HttpCode.internal_server_error)