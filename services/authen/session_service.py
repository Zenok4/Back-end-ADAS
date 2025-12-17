import uuid
import hashlib
from datetime import datetime, timedelta
import logger
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models.sessions import UserSession
from config import SECRET_KEY # Đảm bảo bạn có SECRET_KEY trong config.py

class SessionService:

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash refresh token bằng SHA256."""
        data = (token + SECRET_KEY).encode()
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def _hash_value(value: str) -> str:
        """Hash giá trị bằng SHA256."""
        if value is None:
            value = ""
        data = (value + SECRET_KEY).encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    # [QUAN TRỌNG] Phải có tham số 'request' ở đây để nhận dữ liệu từ LoginService gửi sang
    def create_session(user_id: int, refresh_token: str, request) -> str:
        """
        Tạo session mới trong DB:
        - session_id = UUID
        - lưu hash của refresh_token
        - expires_at = 7 ngày
        """
        session_id = str(uuid.uuid4())
        refresh_token_hash = SessionService._hash_value(refresh_token)

        # Lấy User-Agent từ request headers để bảo mật session
        user_agent = request.headers.get("User-Agent", "")

        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            token_hash=refresh_token_hash,
            user_agent_hash=SessionService._hash_value(user_agent),
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            revoked=False
        )

        db.session.add(session)
        db.session.commit()
        return session_id
    
    @staticmethod
    def validate_session(session_id: str):
        """
        Validate session theo mô hình server-side session.
        """
        if not session_id:
            return None

        try:
            session = UserSession.query.filter_by(
                session_id=session_id,
                revoked=False
            ).first()

            if not session:
                return None

            # Check expiration
            if session.expires_at:
                now = datetime.now()
                if session.expires_at < now:
                    return None

            return session

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception("DB error while validating session_id=%s", session_id)
            return None
        
        except Exception as e:
            db.session.rollback()
            logger.exception(
                "Unexpected error while validating session_id=%s", session_id
            )
            return None

    @staticmethod
    def revoke_session(session_id: str) -> dict:
        """
        Đăng xuất session (revoke).
        """
        session = UserSession.query.filter_by(session_id=session_id, revoked=False).first()
        if not session:
            # Nếu không tìm thấy session hoặc đã revoke rồi thì coi như logout thành công
            return {"success": True, "message": "Session already revoked or not found"}

        session.revoked = True
        db.session.commit()

        return {"success": True, "message": "Logged out successfully"}
    
    @staticmethod
    def check_rate_limit(session) -> bool:
        """
        Rate-limit refresh token:
        - 10 requests / 60s
        """
        now = datetime.now()

        if not session.last_refresh_at or \
        (now - session.last_refresh_at).total_seconds() > 60:
            session.last_refresh_at = now
            session.refresh_count = 1
            db.session.commit()
            return False

        session.refresh_count += 1
        db.session.commit()

        return session.refresh_count > 10

    
    @staticmethod
    def validate_session_context(session, request) -> bool:
        """
        Kiểm tra session có đang dùng đúng thiết bị hay không.
        """
        current_ua = request.headers.get("User-Agent", "")
        if not current_ua:
            # Nếu không có UA, có thể tạm chấp nhận hoặc reject tùy policy
            # Ở đây return False để an toàn
            return False
        
        current_hash = SessionService._hash_value(current_ua)

        if session.user_agent_hash != current_hash:
            # Nếu phát hiện đổi thiết bị/trình duyệt -> Hủy session luôn để bảo mật
            session.revoked = True
            db.session.commit()
            return False

        return True