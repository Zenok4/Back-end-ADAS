# author_endpoint.py
from functools import wraps
from flask import Blueprint, request, jsonify
from middlewares.error_handler import handle_exceptions
from services.author.role_service import RoleService
from services.author.permission_service import PermissionService
from helper.check_constraints_roles import get_current_user_highest_level
from type.http_constants import HttpCode
from helper.normalization_response import response_error
from models.role import Role
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.user import User

author_bp = Blueprint("author", __name__, url_prefix="/author")


# -----------------------
# Exception handler decorator
# -----------------------


# ================== ROLES ==================
@author_bp.route("/users/<int:user_id>/roles/assign", methods=["POST"])
def assign_roles_to_user(user_id):
    """
    Gán nhiều roles cho 1 user.
    - Method: POST
    - URL: /author/users/<user_id>/roles/assign
    - Body: { "role_ids": [1, 2, 3] }
    - Response: { success: true, message: string, code: int, assigned_roles: [...] }
    """
    data = request.get_json()
    role_ids = data.get("role_ids", [])
    result = RoleService.assign_roles_to_user(user_id, role_ids)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/list", methods=["GET"])
def list_roles():
    """
    Lấy danh sách tất cả roles.
    - Method: GET
    - URL: /author/roles/list
    - Body: { "list_permissions": bool } (optional)
    - Response: { success: true, message: string, code: int, roles: [...] }
    """
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        name = request.args.get("name", None, type=str)
        description = request.args.get("description", None, type=str)

        list_permissions_str = request.args.get("list_permissions", "false", type=str)
        is_list_permissions = list_permissions_str.lower() == "true"

        is_active_str = request.args.get("is_active", None, type=str)
        is_active = None
        if is_active_str is not None:
            is_active = is_active_str.lower() == "true"
        result = RoleService.list_roles(
            page=page,
            limit=limit,
            name=name,
            description=description,
            is_active=is_active,
            list_perm=is_list_permissions
        )
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(
            response_error(message=f"Error processing request: {str(e)}", code=HttpCode.internal_server_error)
        ), HttpCode.internal_server_error


@author_bp.route("/roles/<int:role_id>/get", methods=["GET"])
def get_role(role_id):
    """
    Lấy thông tin chi tiết 1 role theo ID.
    - Method: GET
    - URL: /author/roles/<role_id>/get
    - Body (optional): { "list_permissions": true }
    - Response: { success: true, message, code, role: {...} }
    """
    data = request.get_json(silent=True) or {}
    is_list_permissions = request.args.get("list_permissions", "false").lower() == "true"
    # is_list_permissions = bool(data.get("list_permissions", False))
    result = RoleService.get_role_by_id(role_id, include_permissions=is_list_permissions)
    return jsonify(result), result.get("code", HttpCode.success)

@author_bp.route("/roles/get-by-name", methods=["GET"])
def get_role_by_name():
    """
    Lấy thông tin chi tiết 1 role theo tên.
    - Method: GET
    - URL: /author/roles/get-by-name
    - Body: { "name": string, "list_permissions": bool } (required)
    - Response: { success: true, message: string, code: int, role: {...} }
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    is_list_permissions = bool(data.get("list_permissions", False))

    if not name:
        return jsonify(response_error(message="Missing required field: 'name'", code=HttpCode.bad_request)), HttpCode.bad_request

    result = RoleService.get_role_by_name(name, include_permissions=is_list_permissions)
    return jsonify(result), result.get("code", HttpCode.success)



@author_bp.route("/roles/create", methods=["POST"])
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
    is_active = data.get("is_active", True)
    level = data.get("level", 1)

    data = request.get_json() or {}
    # Lấy level của người dùng hiện tại
    current_level = data.get("current_user_level", get_current_user_highest_level())

    if not name:
        return jsonify(response_error(message="Role name is required", code=HttpCode.bad_request)), HttpCode.bad_request
    
    result = RoleService.create_role(
        name,
        description,
        level,
        is_active,
        current_user_level=current_level # Truyền level vào service
    )
    return jsonify(result), result.get("code", HttpCode.created)


@author_bp.route("/roles/<int:role_id>/update", methods=["PUT"])
def update_role(role_id):
    """
    Cập nhật role.
    - Method: PUT
    - URL: /author/roles/<role_id>/update
    - Input JSON: { "name": "...", "description": "...", "level": int, "is_active": boolean } (có thể partial)
    - Trả về: { success: true, message: string, code: int, role: {...} }
    """

    data = request.get_json() or {}
    current_level = data.get("current_user_level", get_current_user_highest_level())
    if "current_user_level" in data:
        data.pop("current_user_level")

    result = RoleService.update_role(
        role_id=role_id, 
        current_user_level=current_level, # Truyền level vào service
        **data
    )
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/<int:role_id>/delete", methods=["DELETE"])
def delete_role(role_id):
    """
    Xóa role.
    - Method: DELETE
    - URL: /author/roles/<role_id>/delete
    - Trả về: { success: true, message: string, code: int, deleted: { id: <role_id> } }
    """
    current_level = request.args.get("current_user_level", type=int, default=get_current_user_highest_level())

    result = RoleService.delete_role(
        role_id=role_id, 
        current_user_level=current_level # Truyền level vào service
    )
    return jsonify(result), result.get("code", HttpCode.success)



@author_bp.route("/users/<int:user_id>/roles/list", methods=["GET"])
def get_user_roles(user_id):
    """
    Lấy danh sách roles của 1 user.
    - Method: GET
    - URL: /author/users/<user_id>/roles/list
    - Body (optional): { "include_permissions": bool }
    - Trả về: { success: true, message: string, code: int, roles: [...] }
    """
    include_permissions = request.args.get("include_permissions", "false").lower() == "true"
    result = RoleService.get_user_roles(user_id, include_permissions)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== PERMISSIONS ==================

@author_bp.route("/permissions/list", methods=["GET"])
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
def list_role_permissions(role_id):
    """
    Lấy danh sách permissions của 1 role.
    - Method: GET
    - URL: /author/roles/<role_id>/permissions/list
    - Trả về: { success: true, message: string, code: int, permissions: [...] }
    """
    result = PermissionService.get_permission_by_code(role_id)
    return jsonify(result), result.get("code", HttpCode.success)


@author_bp.route("/roles/<int:role_id>/permissions/assign", methods=["POST"])
def assign_permissions_to_role(role_id):
    """
    Gán nhiều permission cho 1 role.
    - Method: POST
    - URL: /author/roles/<role_id>/permissions/assign
    - Body: { "perm_ids": [1, 2, 3] }
    - Response: { success: true, message: string, code: int, assigned_permissions: [...] }
    """
    data = request.get_json()
    perm_ids = data.get("perm_ids", [])
    if not perm_ids or not isinstance(perm_ids, list):
        return jsonify(
            response_error(message="perm_ids must be a non-empty list", code=HttpCode.bad_request)
        ), HttpCode.bad_request
    
    result = PermissionService.assign_permissions(role_id, perm_ids)
    return jsonify(result), result.get("code", HttpCode.success)



@author_bp.route("/roles/<int:role_id>/permissions/<int:perm_id>/remove", methods=["DELETE"])
def remove_permission_from_role(role_id, perm_id):
    """
    Gỡ permission khỏi role.
    - Method: DELETE
    - URL: /author/roles/<role_id>/permissions/<perm_id>/remove
    - Trả về: { success: true, message: string, code: int, role: {...} }
    """
    result = PermissionService.remove_permission(role_id, perm_id)
    return jsonify(result), result.get("code", HttpCode.success)
