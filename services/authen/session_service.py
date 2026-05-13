import uuid
import hashlib
import json
from datetime import datetime, timedelta

import logger
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models.sessions import UserSession
from config import SECRET_KEY, REDIS_SESSION_TTL
from redis_client import redis_client

# Key pattern: session:{session_id}
def _session_key(session_id: str) -> str:
    return f"session:{session_id}"

# Key pattern: rate_limit:refresh:{session_id}
def _rate_limit_key(session_id: str) -> str:
    return f"rate_limit:refresh:{session_id}"


class SessionService:

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash refresh token bằng SHA256."""
        data = (token + SECRET_KEY).encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _hash_value(value: str) -> str:
        """Hash giá trị bằng SHA256."""
        data = (value + SECRET_KEY).encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _session_to_dict(session: UserSession) -> dict:
        """Chuyển UserSession thành dict để lưu Redis."""
        return {
            "id": session.id,
            "session_id": session.session_id,
            "user_id": session.user_id,
            "token_hash": session.token_hash,
            "user_agent_hash": session.user_agent_hash,
            "revoked": session.revoked,
            "expires_at": session.expires_at.isoformat() if session.expires_at else None,
            "issued_at": session.issued_at.isoformat() if session.issued_at else None,
        }

    @staticmethod
    def _cache_session(session: UserSession):
        """Lưu session vào Redis cache."""
        key = _session_key(session.session_id)
        payload = json.dumps(SessionService._session_to_dict(session))
        # TTL còn lại tính từ expires_at
        if session.expires_at:
            remaining = int((session.expires_at - datetime.now()).total_seconds())
            ttl = max(remaining, 1)
        else:
            ttl = REDIS_SESSION_TTL
        redis_client.set(key, payload, ex=ttl)

    @staticmethod
    def _invalidate_session_cache(session_id: str):
        """Xóa session khỏi Redis cache."""
        redis_client.delete(_session_key(session_id))

    # ==================== PUBLIC API ====================

    @staticmethod
    def create_session(user_id: int, refresh_token: str, request) -> str:
        """
        Tạo session mới trong DB và cache vào Redis.
        """
        session_id = str(uuid.uuid4())
        refresh_token_hash = SessionService._hash_value(refresh_token)

        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            token_hash=refresh_token_hash,
            user_agent_hash=SessionService._hash_value(
                request.headers.get("User-Agent", "")
            ),
            issued_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            revoked=False,
        )

        db.session.add(session)
        db.session.commit()

        # Cache vào Redis
        SessionService._cache_session(session)

        return session_id

    @staticmethod
    def validate_session(session_id: str):
        """
        Validate session: kiểm tra Redis trước, fallback sang DB.

        Trả về UserSession nếu hợp lệ, None nếu không.
        """
        if not session_id:
            return None

        # 1. Thử lấy từ Redis cache
        key = _session_key(session_id)
        raw = redis_client.get(key)

        if raw:
            try:
                data = json.loads(raw)
                if data.get("revoked"):
                    return None
                expires_at_str = data.get("expires_at")
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if expires_at < datetime.now():
                        redis_client.delete(key)
                        return None
                # Trả về object giả lập đủ field cần thiết
                return _CachedSession(data)
            except (ValueError, KeyError):
                pass  # Cache lỗi → fallback DB

        # 2. Fallback: query DB
        try:
            session = UserSession.query.filter_by(
                session_id=session_id,
                revoked=False,
            ).first()

            if not session:
                return None

            if session.expires_at and session.expires_at < datetime.now():
                return None

            # Warm up cache
            SessionService._cache_session(session)
            return session

        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("DB error while validating session_id=%s", session_id)
            return None
        except Exception:
            db.session.rollback()
            logger.exception("Unexpected error while validating session_id=%s", session_id)
            return None

    @staticmethod
    def revoke_session(session_id: str) -> dict:
        """Đăng xuất session: revoke trong DB và xóa cache Redis."""
        session = UserSession.query.filter_by(
            session_id=session_id, revoked=False
        ).first()

        if not session:
            SessionService._invalidate_session_cache(session_id)
            return {"success": True, "message": "Session already revoked or not found"}

        session.revoked = True
        db.session.commit()

        # Xóa cache
        SessionService._invalidate_session_cache(session_id)

        return {"success": True, "message": "Logged out successfully"}

    @staticmethod
    def check_rate_limit(session) -> bool:
        """
        Rate-limit refresh token dùng Redis:
        - Tối đa 10 requests / 60 giây mỗi session
        """
        key = _rate_limit_key(session.session_id)

        count = redis_client.get(key)
        if count is None:
            redis_client.set(key, 1, ex=60)
            return False

        count = int(count)
        if count >= 10:
            return True

        redis_client.incr(key)
        return False

    @staticmethod
    def validate_session_context(session, request) -> bool:
        """Kiểm tra session có đang dùng đúng thiết bị hay không."""
        current_ua = request.headers.get("User-Agent", "")
        if not current_ua:
            return False

        current_hash = SessionService._hash_value(current_ua)

        if session.user_agent_hash != current_hash:
            # Revoke và xóa cache
            if hasattr(session, '_is_cached') and session._is_cached:
                # Lấy từ DB để revoke
                db_session = UserSession.query.filter_by(
                    session_id=session.session_id
                ).first()
                if db_session:
                    db_session.revoked = True
                    db.session.commit()
            else:
                session.revoked = True
                db.session.commit()

            SessionService._invalidate_session_cache(session.session_id)
            return False

        return True


class _CachedSession:
    """
    Object giả lập UserSession từ dữ liệu Redis cache.
    Dùng để tránh query DB khi session đã được cache.
    """
    _is_cached = True

    def __init__(self, data: dict):
        self.id = data.get("id")
        self.session_id = data.get("session_id")
        self.user_id = data.get("user_id")
        self.token_hash = data.get("token_hash")
        self.user_agent_hash = data.get("user_agent_hash")
        self.revoked = data.get("revoked", False)
        expires_at_str = data.get("expires_at")
        self.expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else None
        issued_at_str = data.get("issued_at")
        self.issued_at = datetime.fromisoformat(issued_at_str) if issued_at_str else None

    def is_active(self) -> bool:
        return not self.revoked and (
            self.expires_at is None or self.expires_at > datetime.now()
        )
