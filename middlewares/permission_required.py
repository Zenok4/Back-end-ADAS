# middlewares/permission_required.py
from functools import wraps, lru_cache
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from type.http_constants import HttpCode
from helper.normalization_response import response_error


# cache permission by user_id
@lru_cache(maxsize=3000)
def cached_permissions(user_id: int):
    """Lấy quyền của người dùng từ dịch vụ và cache chúng."""
    from services.author.permission_service import PermissionService
    perms = PermissionService.get_user_permissions(user_id)
    permissions_list = perms.get('permissions', [])
    
    return tuple(permissions_list)

def clear_permissions_cache():
    """Xóa tất cả các mục đã cache trong lru_cache."""
    cached_permissions.cache_clear()

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
                user_id = identity.get("id") or identity.get("user_id") \
                    if isinstance(identity, dict) else identity
                user_id = int(user_id)
            except Exception:
                return jsonify(response_error(
                    message="Unauthorized",
                    code=HttpCode.unauthorized,
                )), HttpCode.unauthorized

            # Lấy quyền đã cache
            user_perms = cached_permissions(user_id)

            # CHỈ sửa logic lấy code quyền
            permission_codes = {p["code"] for p in user_perms if isinstance(p, dict)}

            # Check permission
            if require_all:
                ok = perm_codes.issubset(permission_codes)
            else:
                ok = bool(perm_codes & permission_codes)

            if not ok:
                return jsonify(response_error(
                    message="Permission Denied",
                    code=HttpCode.forbidden,
                )), HttpCode.forbidden

            return f(*args, **kwargs)
        return wrapper
    return decorator
