import sys
from flask import Blueprint, request, jsonify
from helper.normalization_response import response_error, response_success
from models.user import User
from models.user_role import UserRole
from database import db
from type.http_constants import HttpCode
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_
from services.authen.otp_service import OTPService  # Import OTPService

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    def generate_password_hash(password):
        print("CẢNH BÁO: werkzeug.security không được cài đặt. Mật khẩu không được hash.", file=sys.stderr)
        return password

class UserService:

    # =============== HELPER: LẤY LEVEL CAO NHẤT CỦA USER ===============
    @staticmethod
    def _get_user_max_level(user):
        """
        Lấy level cao nhất trong danh sách roles của user object.
        Trả về 0 nếu user không có role nào.
        """
        if not user or not user.roles:
            return 0
        levels = [r.level for r in user.roles if hasattr(r, 'level')]
        return max(levels) if levels else 0

    # =============== GET ALL USERS ===============
    @staticmethod
    def get_all_users(page=1, limit=20, search=None, is_active=None, role_id=None):
        try:
            query = User.query

            # Logic lọc theo 'search'
            if search:
                search_like = f"%{search}%"
                query = query.filter(
                    or_(
                        (User.username.ilike(search_like)),
                        (User.email.ilike(search_like)),
                        (User.phone.ilike(search_like))
                    )
                )
            
            # Logic lọc theo trạng thái
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            # Logic lọc theo vai trò
            if role_id is not None:
                query = query.join(UserRole, User.id == UserRole.user_id).filter(
                    UserRole.role_id == role_id
                )

            # Đếm tổng số lượng
            total = query.count()
            
            # Phân trang và sắp xếp
            users = (
                query.order_by(User.id.desc())
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )

            # Chuyển đổi sang dict và sắp xếp Role theo level giảm dần để hiển thị đẹp hơn
            user_list = []
            for u in users:
                u_dict = u.to_dict(include_roles=True)
                if "roles" in u_dict and u_dict["roles"]:
                    # Sắp xếp roles: Level cao xếp trước
                    u_dict["roles"] = sorted(
                        u_dict["roles"], 
                        key=lambda x: x.get("level", 0), 
                        reverse=True
                    )
                user_list.append(u_dict)

            payload = {
                "users": user_list,
                "page": page,
                "limit": limit,
                "total": total,
            }
            return response_success(payload, message="Fetched users successfully")

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to get all users: {str(e)}", HttpCode.internal_server_error)


    # =============== GET USER BY ID ===============
    @staticmethod
    def get_user_by_id(user_id: int, include_roles: bool = False):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)
            return response_success(
                user.to_dict(include_roles=include_roles),
                message="Fetched user successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            return response_error(f"Failed to get user: {str(e)}", HttpCode.internal_server_error)


    # =============== GET USER BY USERNAME ===============
    @staticmethod
    def get_user_by_username(username: str, include_roles: bool = False):
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return response_error("User not found", HttpCode.not_found)
            return response_success(
                user.to_dict(include_roles=include_roles),
                message="Fetched user successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            return response_error(f"Failed to get user: {str(e)}", HttpCode.internal_server_error)


    # =============== FILTER USERS BY ACTIVE STATUS ===============
    @staticmethod
    def get_users_by_active(is_active: bool, include_roles: bool = False):
        try:
            users = (
                User.query
                .filter_by(is_active=is_active)
                .order_by(User.id.desc())
                .all()
            )
            return response_success(
                [u.to_dict(include_roles=include_roles) for u in users],
                key="users", 
                message="Fetched users successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            return response_error(f"Failed to get users: {str(e)}", HttpCode.internal_server_error)


    # =============== CREATE USER ===============
    @staticmethod
    def create_user(data):
        try:
            required = ["username", "email", "phone", "password"]
            if not all(data.get(f) for f in required):
                return response_error("Missing required fields", HttpCode.bad_request)

            hashed_password = generate_password_hash(data["password"])
            new_user = User(
                username=data["username"],
                email=data["email"],
                phone=data["phone"],
                password_hash=hashed_password,
                display_name=data.get("display_name", data["username"]) 
            )
            
            db.session.add(new_user)
            db.session.commit()

            return response_success(
                new_user.to_dict(), 
                message="User created successfully",
                code=HttpCode.created
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig).lower()
            if "user.username" in error_message:
                return response_error("Username already exists", HttpCode.bad_request)
            if "email" in error_message:
                return response_error("Email này đã được sử dụng, vui lòng chọn email khác.", HttpCode.bad_request)
            if "phone" in error_message:
                return response_error("Số điện thoại này đã được sử dụng.", HttpCode.bad_request)
            return response_error(f"Duplicate entry error: {error_message}", HttpCode.bad_request)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"An unexpected error occurred: {str(e)}", HttpCode.internal_server_error)


    # =============== UPDATE USER ===============
    @staticmethod
    def update_user(user_id, data, current_user_level=0, is_self_update=False):
        """
        Cập nhật thông tin user.
        - is_self_update (bool): Nếu True, bỏ qua kiểm tra level (dùng cho user tự sửa profile).
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            # === KIỂM TRA LEVEL (Chỉ chạy khi KHÔNG phải tự update) ===
            if not is_self_update:
                target_user_level = UserService._get_user_max_level(user)
                if target_user_level >= current_user_level:
                    return response_error(
                        f"Không đủ quyền hạn. Bạn (Lv.{current_user_level}) không thể chỉnh sửa người dùng có cấp độ cao hơn hoặc bằng ({target_user_level}).", 
                        HttpCode.forbidden
                    )
            # ==========================================================

            # Danh sách các trường được phép update
            allowed_fields = [
                "username", "email", "phone", "display_name",
                "address", "vehicle_name", "license_plate"
            ]

            for key in allowed_fields:
                if key in data: # Chỉ update nếu có trong data gửi lên (kể cả gửi lên None)
                    setattr(user, key, data[key])

            db.session.commit()
            
            return response_success(
                user.to_dict(),
                message="User updated successfully"
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig).lower()
            if "user.username" in error_message:
                return response_error("Username already exists", HttpCode.bad_request)
            if "email" in error_message:
                return response_error("Email này đã được sử dụng, vui lòng chọn email khác.", HttpCode.bad_request)
            if "phone" in error_message:
                return response_error("Số điện thoại này đã được sử dụng.", HttpCode.bad_request)
            return response_error(f"Duplicate entry error: {error_message}", HttpCode.bad_request)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)


    # =============== DELETE USER ===============
    @staticmethod
    def delete_user(user_id, current_user_level=0):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            # === KIỂM TRA LEVEL ===
            target_user_level = UserService._get_user_max_level(user)
            if target_user_level >= current_user_level:
                return response_error(
                    f"Không đủ quyền hạn. Bạn (Lv.{current_user_level}) không thể xóa người dùng có cấp độ cao hơn hoặc bằng ({target_user_level}).", 
                    HttpCode.forbidden
                )
            # ======================

            db.session.delete(user)
            db.session.commit()
            return response_success({"id": user_id}, message="User deleted")

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Delete failed: {str(e)}", HttpCode.internal_server_error)


    # =============== TOGGLE USER STATUS ===============
    @staticmethod
    def toggle_status(user_id, data, current_user_level=0):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)
            
            # === KIỂM TRA LEVEL ===
            target_user_level = UserService._get_user_max_level(user)
            if target_user_level >= current_user_level:
                return response_error(
                    f"Không đủ quyền hạn. Bạn không thể thay đổi trạng thái của người dùng có cấp độ cao hơn hoặc bằng ({target_user_level}).", 
                    HttpCode.forbidden
                )
            # ======================

            is_active = data.get("is_active")
            if is_active is None:
                return response_error("Missing field 'is_active'", HttpCode.bad_request)

            user.is_active = bool(is_active)
            db.session.commit()

            return response_success(
                user.to_dict(),
                message="User status updated successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Toggle status failed: {str(e)}", HttpCode.internal_server_error)


    # =============== CHANGE PASSWORD (CÓ OTP) ===============
    @staticmethod
    def change_password(user_id, data):
        """
        Đổi mật khẩu: Yêu cầu pass cũ + pass mới + OTP.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            old_password = data.get("old_password")
            new_password = data.get("new_password")
            otp_code = data.get("otp_code")  # <--- Bắt buộc có OTP

            if not old_password or not new_password or not otp_code:
                return response_error("Missing required fields (old_password, new_password, otp_code)", HttpCode.bad_request)

            # 1. Kiểm tra mật khẩu cũ
            from werkzeug.security import check_password_hash
            if not check_password_hash(user.password_hash, old_password):
                return response_error("Old password is incorrect", HttpCode.bad_request)

            # 2. Kiểm tra OTP
            # Ưu tiên email, nếu không có thì dùng phone
            identifier = user.email if user.email else user.phone
            if not identifier:
                 return response_error("User has no contact info to verify OTP", HttpCode.bad_request)

            # Dùng purpose='change_password'
            check_otp = OTPService.validate_otp_only(identifier, otp_code, purpose="change_password")
            if not check_otp["valid"]:
                return response_error(check_otp["error"], HttpCode.bad_request)

            # 3. Kiểm tra pass mới có trùng pass cũ không
            if check_password_hash(user.password_hash, new_password):
                return response_error("New password must be different from old password", HttpCode.bad_request)

            # 4. Hash và lưu mật khẩu mới
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return response_success(
                {"id": user_id},
                message="Password changed successfully"
            )

        except IntegrityError as e:
            db.session.rollback()
            return response_error(f"Integrity error: {str(e.orig)}", HttpCode.bad_request)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)

        except Exception as e:
            db.session.rollback()
            return response_error(f"Change password failed: {str(e)}", HttpCode.internal_server_error)

    # =============== GỬI OTP ĐỔI MẬT KHẨU ===============
    @staticmethod
    def send_otp_for_change_password(user_id, channel="email"):
        """
        Gửi OTP về email hoặc sđt để đổi mật khẩu.
        channel: 'email' hoặc 'phone'
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)
            
            identifier = None
            type_id = None

            # Logic chọn kênh gửi
            if channel == "email":
                if not user.email:
                    return response_error("Tài khoản này chưa cập nhật Email.", HttpCode.bad_request)
                identifier = user.email
                type_id = "email"
            elif channel == "phone":
                if not user.phone:
                    return response_error("Tài khoản này chưa cập nhật Số điện thoại.", HttpCode.bad_request)
                identifier = user.phone
                type_id = "phone"
            else:
                # Fallback: Tự động chọn nếu gửi channel linh tinh
                if user.email:
                    identifier = user.email
                    type_id = "email"
                elif user.phone:
                    identifier = user.phone
                    type_id = "phone"
            
            if not identifier:
                 return response_error("User has no contact info to send OTP", HttpCode.bad_request)

            # Gửi OTP với purpose='change_password'
            OTPService.create_and_send_otp(identifier, type_id, purpose="change_password")
            
            return response_success(message=f"OTP sent to {identifier}")
        except Exception as e:
            return response_error(f"Error sending OTP: {str(e)}", HttpCode.internal_server_error)