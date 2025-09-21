import uuid
import hashlib
from datetime import datetime, timedelta, timezone

from database import db
from models.sessions import UserSession

from config import SECRET_KEY


class SessionService:

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash refresh token bằng SHA256."""
        data = (token + SECRET_KEY).encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def create_session(user_id: int, refresh_token: str) -> str:
        """
        Tạo session mới trong DB:
        - session_id = UUID
        - lưu hash của refresh_token
        - expires_at = 7 ngày
        """
        session_id = str(uuid.uuid4())
        refresh_token_hash = SessionService._hash_token(refresh_token)

        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            token_hash=refresh_token_hash,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            revoked=False
        )

        db.session.add(session)
        db.session.commit()
        return session_id

    @staticmethod
    def validate_session(refresh_token: str) -> bool:
        """
        Kiểm tra refresh_token còn hợp lệ:
        - Hash refresh_token có trong DB
        - revoked = False
        - expires_at > hiện tại
        """
        token_hash = SessionService._hash_token(refresh_token)

        session = UserSession.query.filter_by(token_hash=token_hash, revoked=False).first()

        if not session:
            return False
        if session.expires_at and session.expires_at < datetime.now(timezone.utc):
            return False

        return True

    @staticmethod
    def revoke_session(session_id: str) -> dict:
        """
        Đăng xuất session (revoke).
        """
        session = UserSession.query.filter_by(session_id=session_id, revoked=False).first()
        if not session:
            return {"error": "Session not found or already revoked"}

        session.revoked = True
        db.session.commit()

        return {"success": True, "message": "Logged out successfully"}
