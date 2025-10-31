# services/user_service.py (ĐÃ SỬA)
from helper.normalization_response import response_error, response_success
from models.user import User
from sqlalchemy.exc import SQLAlchemyError
from database import db
from type.http_constants import HttpCode

# Thêm import để băm mật khẩu
try:
    from werkzeug.security import generate_password_hash
except ImportError:
    print("CẢNH BÁO: werkzeug.security chưa được cài đặt. Mật khẩu sẽ không được băm!")
    def generate_password_hash(password):
        return password

class UserService:
    """
    Service xử lý toàn bộ nghiệp vụ liên quan đến người dùng.
    ĐÃ SỬA LẠI: Bỏ 'key="user"' để khớp với UserResponse type
    """

    # ================== GET ALL ==================
    @staticmethod
    def get_all_users(page=1, limit=20, keyword=""):
        """
        Trả về response chuẩn cho PaginatedUsersResponse
        """
        try:
            query = User.query

            if keyword:
                keyword_like = f"%{keyword}%"
                query = query.filter(
                    (User.username.ilike(keyword_like)) |
                    (User.email.ilike(keyword_like)) |
                    (User.phone.ilike(keyword_like))
                )

            total = query.count()
            users = (
                query.order_by(User.id.desc())
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )

            # ===================================
            # == BẮT ĐẦU SỬA: Thêm include_roles=True ==
            # ===================================
            # Sửa dòng này để lấy thông tin roles ngay tại list
            user_list = [u.to_dict(include_roles=True) for u in users]
            # ===================================
            # == KẾT THÚC SỬA ==
            # ===================================

            # Dữ liệu trả về (khớp với PaginatedUsersResponse)
            payload = {
                "users": user_list,
                "page": page,
                "limit": limit,
                "total": total,
            }
            
            # Trả về { data: { users: [...], page: ... } }
            return response_success(payload, message="Fetched users successfully")

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to get all users: {str(e)}", HttpCode.internal_server_error)


    @staticmethod
    def get_user_by_id(user_id: int, include_roles: bool = False):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)
            
            # SỬA: Đã bỏ key="user"
            # Trả về { data: UserData }
            return response_success(
                user.to_dict(include_roles=include_roles),
                message="Fetched user successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            return response_error(f"Failed to get user: {str(e)}", HttpCode.internal_server_error)


    # ================== GET BY USERNAME ==================
    @staticmethod
    def get_user_by_username(username: str, include_roles: bool = False):
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return response_error("User not found", HttpCode.not_found)
            
            # SỬA: Đã bỏ key="user"
            return response_success(
                user.to_dict(include_roles=include_roles),
                message="Fetched user successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            return response_error(f"Failed to get user: {str(e)}", HttpCode.internal_server_error)


    # ================== FILTER BY ACTIVE STATUS ==================
    @staticmethod
    def get_users_by_active(is_active: bool, include_roles: bool = False):
        try:
            users = (
                User.query
                .filter_by(is_active=is_active)
                .order_by(User.id.desc())
                .all()
            )
            # SỬA: Dùng response_success chuẩn (khớp với frontend)
            return response_success(
                [u.to_dict(include_roles=include_roles) for u in users],
                key="users", # Giữ key="users" vì đây là 1 danh sách
                message="Fetched users successfully"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            return response_error(f"Failed to get users: {str(e)}", HttpCode.internal_server_error)



    # ================== CREATE ==================
    @staticmethod
    def create_user(data):
        try:
            required = ["username", "email", "phone", "password"]
            if not all(data.get(f) for f in required):
                return response_error("Missing required fields", HttpCode.bad_request)

            if User.query.filter_by(username=data["username"]).first():
                return response_error("Username already exists", HttpCode.bad_request)
            if User.query.filter_by(email=data["email"]).first():
                return response_error("Email already exists", HttpCode.bad_request)

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

            # SỬA: Đã bỏ key="user"
            # Trả về { data: UserData }
            return response_success(
                new_user.to_dict(), 
                message="User created successfully",
                code=HttpCode.created
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"An unexpected error occurred: {str(e)}", HttpCode.internal_server_error)


    # ================== UPDATE ==================
    @staticmethod
    def update_user(user_id, data):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            for key in ["username", "email", "phone", "display_name"]:
                if key in data and data[key]:
                    setattr(user, key, data[key])

            db.session.commit()
            
            # SỬA: Đã bỏ key="user"
            return response_success(
                user.to_dict(),
                message="User updated successfully"
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)


    # ================== DELETE ==================
    @staticmethod
    def delete_user(user_id):
        # Hàm này không trả về data, giữ nguyên
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            db.session.delete(user)
            db.session.commit()
            return response_success({"id": user_id}, message="User deleted")

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Delete failed: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def toggle_status(user_id, data):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            is_active = data.get("is_active")
            if is_active is None:
                return response_error("Missing field 'is_active'", HttpCode.bad_request)

            user.is_active = bool(is_active)
            db.session.commit()

            # SỬA: Đã bỏ key="user"
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