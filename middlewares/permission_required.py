# middlewares/permission_required.py
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from services.author.permission_service import PermissionService
from type.http_constants import HttpCode
from helper.normalization_response import response_success, response_error

def permission_required(*perm_codes, require_all: bool = False):
    """
    Middleware kiểm tra quyền:
    - perm_codes: danh sách các permission code.
    - require_all: nếu True thì yêu cầu có tất cả, nếu False chỉ cần 1 trong số đó.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = None
            try:
                verify_jwt_in_request(optional=True)
                identity = get_jwt_identity()
                if isinstance(identity, dict):
                    user_id = identity.get("id") or identity.get("user_id")
                else:
                    user_id = identity
            except Exception:
                user_id = None

            if not user_id:
                user_id = request.headers.get("X-User-Id")

            if not user_id:
                return jsonify(
                    response_error(
                        message="Unauthorized",
                        code=HttpCode.unauthorized
                    )
                ), HttpCode.unauthorized

            try:
                user_id = int(user_id)
            except Exception:
                return jsonify(
                    response_error(
                        message="Invalid user id",
                        code=HttpCode.bad_request
                    )
                ), HttpCode.bad_request

            user_perms = PermissionService.get_user_permissions(user_id)

            if require_all:
                ok = all(code in user_perms for code in perm_codes)
            else:
                ok = any(code in user_perms for code in perm_codes)

            if not ok:
                return jsonify(
                    response_error(
                        message="Access denied: Insufficient permissions",
                        code=HttpCode.forbidden
                    )
                ), HttpCode.forbidden

            return f(*args, **kwargs)
        return wrapper
    return decorator
