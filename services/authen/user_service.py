# services/authen/user_service.py
from datetime import datetime, timezone
from models.user import User
from models.sessions import UserSession

class UserService:
    @staticmethod
    def get_user_by_session(session_id: str):
        """
        Lấy thông tin user dựa trên session_id.
        - Kiểm tra session có hợp lệ không (tồn tại, chưa revoked, chưa hết hạn).
        - Trả về dict thông tin user nếu ok, hoặc {error} nếu fail.
        """
        session = UserSession.query.filter_by(session_id=session_id).first()

        if not session:
            return {"error": "Session not found"}

        if session.revoked:
            return {"error": "Session revoked"}

        if session.expires_at and session.expires_at < datetime.now(timezone.utc):
            return {"error": "Session expired"}

        user = User.query.get(session.user_id)
        if not user:
            return {"error": "User not found"}

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name,
                "created_at": user.created_at,
            }
        }
