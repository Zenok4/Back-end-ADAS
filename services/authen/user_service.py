import datetime
from helper.normalization_response import response_error, response_success
from models.user import User
from database import db
from type.http_constants import HttpCode
from sqlalchemy.exc import SQLAlchemyError, IntegrityError 

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    def generate_password_hash(password):
        return password



class UserService:

    # =============== GET ALL USERS ===============
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

            payload = {
                "users": [u.to_dict(include_roles=True) for u in users],
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
            if user_id is None:
                return response_error("User ID is required", HttpCode.bad_request)
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
            if "user.email" in error_message:
                return response_error("Email already exists", HttpCode.bad_request)
            if "user.phone" in error_message:
                return response_error("Phone already exists", HttpCode.bad_request)
            return response_error(f"Duplicate entry error: {error_message}", HttpCode.bad_request)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"An unexpected error occurred: {str(e)}", HttpCode.internal_server_error)


    # =============== UPDATE USER ===============
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
            
            return response_success(
                user.to_dict(),
                message="User updated successfully"
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig).lower()
            if "user.username" in error_message:
                return response_error("Username already exists", HttpCode.bad_request)
            if "user.email" in error_message:
                return response_error("Email already exists", HttpCode.bad_request)
            if "user.phone" in error_message:
                return response_error("Phone already exists", HttpCode.bad_request)
            return response_error(f"Duplicate entry error: {error_message}", HttpCode.bad_request)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)


    # =============== DELETE USER ===============
    @staticmethod
    def delete_user(user_id):
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


    # =============== TOGGLE USER STATUS ===============
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


    # =============== CHANGE PASSWORD ===============
    @staticmethod
    def change_password(user_id, data):
        try:
            user = User.query.get(user_id)
            if not user:
                return response_error("User not found", HttpCode.not_found)

            old_password = data.get("old_password")
            new_password = data.get("new_password")

            if not old_password or not new_password:
                return response_error("Missing required fields", HttpCode.bad_request)

            # Kiểm tra mật khẩu cũ
            from werkzeug.security import check_password_hash
            if not check_password_hash(user.password_hash, old_password):
                return response_error("Old password is incorrect", HttpCode.bad_request)

            # Không cho phép đổi sang mật khẩu cũ (optional)
            if check_password_hash(user.password_hash, new_password):
                return response_error("New password must be different from old password", HttpCode.bad_request)

            # Hash mật khẩu mới
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

