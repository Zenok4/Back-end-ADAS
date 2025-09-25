from datetime import datetime
from models.user import User
from models.sessions import UserSession
from helper.normalization_response import response_success, response_error
from pytz import UTC
from type.http_constants import HttpCode

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
            return response_error(
                message="Session not found",
                code=HttpCode.unauthorized
            )

        if session.revoked:
            return response_error(
                message="Session revoked",
                code=HttpCode.unauthorized,
            )

        # Đảm bảo session.expires_at là offset-aware
        expires_at = session.expires_at
        if expires_at and not expires_at.tzinfo:  # Kiểm tra nếu expires_at là naive
            expires_at = expires_at.replace(tzinfo=UTC)  # Thêm múi giờ UTC

        if expires_at and expires_at < datetime.now():
            return response_error(message="Session expired", code=HttpCode.unauthorized)

        user = User.query.get(session.user_id)
        if not user:
            return response_error(message="User not found", code=HttpCode.not_found)


        return response_success(data=user.to_dict(), key="user", message="Get infomation successfull", code=HttpCode.success)
    