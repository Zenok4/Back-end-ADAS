from flask import Blueprint, request, jsonify
from services.authen.user_service import UserService
from type.http_constants import HttpCode
from helper.normalization_response import response_success, response_error

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

# ================== LIST ==================
@user_bp.route("/list", methods=["GET"])
def list_users():
    """
    Lấy danh sách người dùng (có phân trang và tìm kiếm)
    - Query params: page, limit, keyword
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        keyword = request.args.get("keyword", "")
        result = UserService.get_all_users(page, limit, keyword)

        return jsonify(response_success(
            data=result,
            message="Fetched user list successfully",
            code=HttpCode.success
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== DETAIL BY ID ==================
@user_bp.route("/id/<int:user_id>", methods=["GET"])
def get_user_detail(user_id):
    """
    Lấy thông tin chi tiết người dùng theo ID.
    - Method: GET
    - URL: /users/id/<user_id>
    - Body (optional): { "include_roles": bool }
    """
    data = request.get_json(silent=True) or {}
    include_roles = bool(data.get("include_roles", False))

    result = UserService.get_user_by_id(user_id, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== DETAIL BY USERNAME ==================
@user_bp.route("/username/<string:username>", methods=["GET"])
def get_user_by_username(username):
    """
    Lấy thông tin người dùng theo username.
    - Method: GET
    - URL: /users/username/<username>
    - Body (optional): { "include_roles": bool }
    """
    data = request.get_json(silent=True) or {}
    include_roles = bool(data.get("include_roles", False))

    result = UserService.get_user_by_username(username, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== FILTER BY ACTIVE STATUS ==================
@user_bp.route("/active/<string:is_active>", methods=["GET"])
def list_users_by_active(is_active):
    """
    Lấy danh sách người dùng theo trạng thái hoạt động.
    - Method: GET
    - URL: /users/active/<true|false>
    - Body (optional): { "include_roles": bool }
    """
    data = request.get_json(silent=True) or {}
    include_roles = bool(data.get("include_roles", False))

    is_active_bool = is_active.lower() == "true"
    result = UserService.get_users_by_active(is_active_bool, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== CREATE ==================
@user_bp.route("/create", methods=["POST"])
def create_user():
    """
    Tạo mới người dùng.
    - Input JSON: { "username": "...", "email": "...", "phone": "...", "password": "..." }
    """
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.create_user(data)
        if "error" in result:
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        return jsonify(response_success(
            data=result["data"],
            message="User created successfully",
            code=HttpCode.created
        )), HttpCode.created

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== UPDATE ==================
@user_bp.route("/update/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Cập nhật thông tin người dùng.
    - Input JSON: { "username": "...", "email": "...", "phone": "..." }
    """
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.update_user(user_id, data)
        if "error" in result:
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        return jsonify(response_success(
            data=result["data"],
            message="User updated successfully",
            code=HttpCode.success
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== DELETE ==================
@user_bp.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Xóa người dùng theo ID.
    """
    try:
        result = UserService.delete_user(user_id)
        if not result.get("success", False):
            return jsonify(response_error(
                message=result.get("error", "User not found"),
                code=HttpCode.not_found
            )), HttpCode.not_found

        return jsonify(response_success(
            message="User deleted successfully",
            code=HttpCode.success
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== TOGGLE STATUS ==================
@user_bp.route("/status/<int:user_id>", methods=["PATCH"])
def toggle_user_status(user_id):
    """
    Thay đổi trạng thái hoạt động của người dùng (active/inactive).
    - Input JSON: { "is_active": true/false }
    """
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.toggle_status(user_id, data)
        if "error" in result:
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        return jsonify(response_success(
            data=result["data"],
            message="User status updated successfully",
            code=HttpCode.success
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error
