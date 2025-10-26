from models.user import User
from sqlalchemy.exc import SQLAlchemyError
from database import db

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


    # ================== GET BY ID ==================
    @staticmethod
    def get_user_by_id(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            return user.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}


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
