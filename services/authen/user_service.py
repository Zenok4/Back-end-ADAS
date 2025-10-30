from helper.normalization_response import response_error, response_success
from models.user import User
from sqlalchemy.exc import SQLAlchemyError
from database import db
from type.http_constants import HttpCode

class UserService:
    """
    Service xử lý toàn bộ nghiệp vụ liên quan đến người dùng.
    Bao gồm: CRUD, tìm kiếm, phân trang.
    """

    # ================== GET ALL ==================
    @staticmethod
    def get_all_users(page=1, limit=20, keyword=""):
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

            user_list = [u.to_dict() for u in users]

            return {
                "data": {
                    "users": user_list,
                    "page": page,
                    "limit": limit,
                    "total": total,
                }
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}


    @staticmethod
    def get_user_by_id(user_id: int, include_roles: bool = False):
        """
        Lấy thông tin người dùng theo ID.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)
            return response_success(
                user.to_dict(include_roles=include_roles),
                key="user",
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
        """
        Lấy thông tin người dùng theo username.
        """
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return response_error("User not found", HttpCode.success)
            return response_success(
                user.to_dict(include_roles=include_roles),
                key="user",
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
        """
        Lấy danh sách người dùng theo trạng thái hoạt động.
        """
        try:
            users = (
                User.query
                .filter_by(is_active=is_active)
                .order_by(User.id.desc())
                .all()
            )
            if not users:
                return response_success([], key="users", message="No users found with given status")
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



    # ================== CREATE ==================
    @staticmethod
    def create_user(data):
        try:
            required = ["username", "email", "phone", "password"]
            if not all(data.get(f) for f in required):
                return {"error": "Missing required fields"}

            # Check tồn tại
            if User.query.filter_by(username=data["username"]).first():
                return {"error": "Username already exists"}
            if User.query.filter_by(email=data["email"]).first():
                return {"error": "Email already exists"}

            new_user = User.create_user(
                username=data["username"],
                email=data["email"],
                phone=data["phone"],
                password=data["password"],
            )

            db.session.add(new_user)
            db.session.commit()

            return {"data": new_user.to_dict()}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}


    # ================== UPDATE ==================
    @staticmethod
    def update_user(user_id, data):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            for key in ["username", "email", "phone"]:
                if key in data and data[key]:
                    setattr(user, key, data[key])

            db.session.commit()
            return {"data": user.to_dict()}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}


    # ================== DELETE ==================
    @staticmethod
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found", "success": False}

            db.session.delete(user)
            db.session.commit()
            return {"success": True}

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def toggle_status(user_id, data):
        """Kích hoạt / khóa tài khoản người dùng."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            is_active = data.get("is_active")
            if is_active is None:
                return {"error": "Missing field 'is_active'"}

            user.is_active = bool(is_active)
            db.session.commit()

            return {"data": user.to_dict()}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
