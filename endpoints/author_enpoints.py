# author_endpoint.py
from functools import wraps
from flask import Blueprint, request, jsonify
from middlewares.error_handler import handle_exceptions
from services.author.role_service import RoleService
from services.author.permission_service import PermissionService
from type.http_constants import HttpCode
from helper.normalization_response import response_error, response_success

author_bp = Blueprint("author", __name__, url_prefix="/author")


# -----------------------
# Exception handler decorator
# -----------------------


# ================== ROLES ==================
@author_bp.route("/users/<int:user_id>/roles/<int:role_id>/assign", methods=["POST"])
@handle_exceptions
def assign_role_to_user(user_id, role_id):
    """
    Gán role cho user.
    - Method: POST
    - URL: /author/users/<user_id>/roles/<role_id>
    - Response: { success: true, message: string, code: int, user_role_binding: {...} }
    """
    result = RoleService.assign_role_to_user(user_id, role_id)
    return jsonify(result), result.get("code", HttpCode.success)

@author_bp.route("/roles/list", methods=["GET"])
@handle_exceptions
def list_roles():
    """
    Lấy danh sách tất cả roles.
    - Method: GET
    - URL: /author/roles/list
    - Response: { success: true, message: string, code: int, roles: [...] }
    """
    result = RoleService.list_roles()
    return jsonify(result), result.get("code", HttpCode.success)

@author_bp.route("/roles/<int:role_id>/get", methods=["GET"])
@handle_exceptions
def get_role(role_id):
    """
    Lấy thông tin chi tiết 1 role.
    - Method: GET
    - URL: /author/roles/<role_id>/get
    - Response: { success: true, message, code, role: {...} }
    """
    result = RoleService.get_role_by_id(role_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/create", methods=["POST"])
@handle_exceptions
def create_role():
    """
    Tạo role mới.
    - Method: POST
    - URL: /author/roles/create
    - Input JSON: { "name": "...", "description": "..." }
    - Trả về: { success: true, message: string, code: int, role: {...} }
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify(
            response_error(message="Role name required", code=HttpCode.bad_request)
        ), HttpCode.bad_request

    result = RoleService.create_role(name, description)
    return jsonify(result), result.get("code", HttpCode.created)


@author_bp.route("/roles/<int:role_id>/update", methods=["PUT"])
@handle_exceptions
def update_role(role_id):
    """
    Cập nhật role.
    - Method: PUT
    - URL: /author/roles/<role_id>/update
    - Input JSON: { "name": "...", "description": "..." } (có thể partial)
    - Trả về: { success: true, message: string, code: int, role: {...} }
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify(
            response_error(message="No update data provided", code=HttpCode.bad_request)
        ), HttpCode.bad_request

    result = RoleService.update_role(role_id, **data)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/<int:role_id>/delete", methods=["DELETE"])
@handle_exceptions
def delete_role(role_id):
    """
    Xóa role.
    - Method: DELETE
    - URL: /author/roles/<role_id>/delete
    - Trả về: { success: true, message: string, code: int, deleted: { id: <role_id> } }
    """
    result = RoleService.delete_role(role_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/users/<int:user_id>/roles/list", methods=["GET"])
@handle_exceptions
def get_user_roles(user_id):
    """
    Lấy danh sách roles của 1 user.
    - Method: GET
    - URL: /author/users/<user_id>/roles/list
    - Trả về: { success: true, message: string, code: int, roles: [...] }
    """
    result = RoleService.get_user_roles(user_id)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== PERMISSIONS ==================

@author_bp.route("/permissions/list", methods=["GET"])
@handle_exceptions
def list_permissions():
    """
    Lấy danh sách tất cả permissions.
    - Method: GET
    - URL: /author/permissions/list
    - Trả về: { success: true, message: string, code: int, permissions: [...] }
    """
    result = PermissionService.list_permissions()
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/permissions/<int:perm_id>/get", methods=["GET"])
@handle_exceptions
def get_permission(perm_id):
    """
    Lấy chi tiết 1 permission.
    - Method: GET
    - URL: /author/permissions/<perm_id>/get
    - Trả về: { success: true, message: string, code: int, permission: {...} }
    """
    result = PermissionService.get_permission_by_id(perm_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/permissions/create", methods=["POST"])
@handle_exceptions
def create_permission():
    """
    Tạo permission mới.
    - Method: POST
    - URL: /author/permissions/create
    - Input JSON: { "code": "...", "title": "...", "description": "...", "group_id": 1 }
    - Trả về: { success: true, message: string, code: int, permission: {...} }
    """
    data = request.get_json(silent=True) or {}
    code = data.get("code")
    title = data.get("title")
    description = data.get("description")
    group_id = data.get("group_id")

    if not code or not title:
        return (
            jsonify(response_error(message="Code and Title required", code=HttpCode.bad_request)),
            HttpCode.bad_request,
        )

    result = PermissionService.create_permission(code, title, description, group_id)
    return jsonify(result), result.get("code", HttpCode.created)


@author_bp.route("/permissions/<int:perm_id>/update", methods=["PUT"])
@handle_exceptions
def update_permission(perm_id):
    """
    Cập nhật permission.
    - Method: PUT
    - URL: /author/permissions/<perm_id>/update
    - Input JSON: { "title": "...", "description": "..." } (partial OK)
    - Trả về: { success: true, message: string, code: int, permission: {...} }
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify(response_error(message="No update data provided", code=HttpCode.bad_request)), HttpCode.bad_request

    result = PermissionService.update_permission(perm_id, **data)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/permissions/<int:perm_id>/delete", methods=["DELETE"])
@handle_exceptions
def delete_permission(perm_id):
    """
    Xóa permission.
    - Method: DELETE
    - URL: /author/permissions/<perm_id>/delete
    - Trả về: { success: true, message: string, code: int, deleted: { id: perm_id } }
    """
    result = PermissionService.delete_permission(perm_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/users/<int:user_id>/permissions/list", methods=["GET"])
@handle_exceptions
def get_user_permissions(user_id):
    """
    Lấy danh sách permissions của 1 user (từ roles của user).
    - Method: GET
    - URL: /author/users/<user_id>/permissions/list
    - Trả về: { success: true, message: string, code: int, permissions: [...] }
    """
    result = PermissionService.get_user_permissions(user_id)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== ROLE <-> PERMISSION MAPPING ==================

@author_bp.route("/roles/<int:role_id>/permissions/list", methods=["GET"])
@handle_exceptions
def list_role_permissions(role_id):
    """
    Lấy danh sách permissions của 1 role.
    - Method: GET
    - URL: /author/roles/<role_id>/permissions/list
    - Trả về: { success: true, message: string, code: int, permissions: [...] }
    """
    result = PermissionService.get_permissions_by_role(role_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/<int:role_id>/permissions/<int:perm_id>/assign", methods=["POST"])
@handle_exceptions
def assign_permission_to_role(role_id, perm_id):
    """
    Gán permission cho role.
    - Method: POST
    - URL: /author/roles/<role_id>/permissions/<perm_id>/assign
    - Trả về: { success: true, message: string, code: int, role: {...} }
    """
    result = PermissionService.assign_permission(role_id, perm_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/<int:role_id>/permissions/<int:perm_id>/remove", methods=["DELETE"])
@handle_exceptions
def remove_permission_from_role(role_id, perm_id):
    """
    Gỡ permission khỏi role.
    - Method: DELETE
    - URL: /author/roles/<role_id>/permissions/<perm_id>/remove
    - Trả về: { success: true, message: string, code: int, role: {...} }
    """
    result = PermissionService.remove_permission(role_id, perm_id)
    return jsonify(result), result.get("code", HttpCode.success)
