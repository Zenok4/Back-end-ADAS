# middlewares/permission_required.py
import json
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from type.http_constants import HttpCode
from helper.normalization_response import response_error
from redis_client import redis_client
from config import REDIS_PERMISSION_TTL

# Key pattern: permission:{user_id}
def _permission_key(user_id: int) -> str:
    return f"permission:{user_id}"


def cached_permissions(user_id: int) -> tuple:
    """
    Lấy quyền của người dùng, ưu tiên Redis cache.
    TTL mặc định: REDIS_PERMISSION_TTL giây (5 phút).
    """
    key = _permission_key(user_id)
    raw = redis_client.get(key)

    if raw:
        try:
            return tuple(json.loads(raw))
        except (ValueError, TypeError):
            pass

    # Cache miss → query DB
    from services.author.permission_service import PermissionService
    perms = PermissionService.get_user_permissions(user_id)
    permissions_list = perms.get("permissions", [])

    redis_client.set(key, json.dumps(permissions_list), ex=REDIS_PERMISSION_TTL)
    return tuple(permissions_list)


def clear_permissions_cache(user_id: int = None):
    """
    Xóa permission cache.
    - Nếu truyền user_id: xóa cache của user đó.
    - Nếu không: xóa toàn bộ permission cache (dùng pattern scan).
    """
    if user_id is not None:
        redis_client.delete(_permission_key(user_id))
    else:
        # Xóa tất cả key khớp pattern permission:*
        keys = redis_client.keys("permission:*")
        if keys:
            redis_client.delete(*keys)


def permission_required(*perm_codes, require_all=False):
    perm_codes = set(perm_codes)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            """Middleware kiểm tra quyền truy cập của người dùng."""

            # Lấy user ID từ JWT
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                user_id = (
                    identity.get("id") or identity.get("user_id")
                    if isinstance(identity, dict)
                    else identity
                )
                user_id = int(user_id)
            except Exception:
                return jsonify(
                    response_error(message="Unauthorized", code=HttpCode.unauthorized)
                ), HttpCode.unauthorized

            # Lấy quyền (từ Redis cache hoặc DB)
            user_perms = cached_permissions(user_id)
            permission_codes = {
                p["code"] for p in user_perms if isinstance(p, dict)
            }

            # Kiểm tra quyền
            if require_all:
                ok = perm_codes.issubset(permission_codes)
            else:
                ok = bool(perm_codes & permission_codes)

            if not ok:
                return jsonify(
                    response_error(message="Permission Denied", code=HttpCode.forbidden)
                ), HttpCode.forbidden

            return f(*args, **kwargs)

        return wrapper

    return decorator
