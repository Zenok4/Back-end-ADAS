# endpoints/usermanage_endpoints.py
from flask import Blueprint, request, jsonify
from services.authen.user_service import UserService
from type.http_constants import HttpCode
from helper.normalization_response import response_error # Chỉ import response_error để dùng trong exception

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

# ================== LIST ==================
@user_bp.route("/list", methods=["GET"])
def list_users():
    """
    Lấy danh sách người dùng (có phân trang và tìm kiếm)
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        keyword = request.args.get("keyword", "")
        
        # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
        result = UserService.get_all_users(page, limit, keyword)
        return jsonify(result), result.get("code", HttpCode.success)

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
    """
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"

    # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
    result = UserService.get_user_by_id(user_id, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== DETAIL BY USERNAME ==================
@user_bp.route("/username/<string:username>", methods=["GET"])
def get_user_by_username(username):
    """
    Lấy thông tin người dùng theo username.
    """
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"

    # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
    result = UserService.get_user_by_username(username, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== FILTER BY ACTIVE STATUS ==================
@user_bp.route("/active/<string:is_active>", methods=["GET"])
def list_users_by_active(is_active):
    """
    Lấy danh sách người dùng theo trạng thái hoạt động.
    """
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"

    is_active_bool = is_active.lower() == "true"
    
    # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
    result = UserService.get_users_by_active(is_active_bool, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== CREATE ==================
@user_bp.route("/create", methods=["POST"])
def create_user():
    """
    Tạo mới người dùng.
    """
    data = request.get_json(silent=True) or {}
    try:
        # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
        result = UserService.create_user(data)
        
        # SỬA: Kiểm tra lỗi chuẩn
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)

        return jsonify(result), result.get("code", HttpCode.created)

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
    """
    data = request.get_json(silent=True) or {}
    try:
        # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
        result = UserService.update_user(user_id, data)
        
        # SỬA: Kiểm tra lỗi chuẩn
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)

        return jsonify(result), result.get("code", HttpCode.success)

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
        # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
        result = UserService.delete_user(user_id)
        
        if not result.get("success", False):
            return jsonify(result), result.get("code", HttpCode.not_found)

        return jsonify(result), result.get("code", HttpCode.success)

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
    """
    data = request.get_json(silent=True) or {}
    try:
        # SỬA: Service đã trả về response chuẩn, chỉ cần jsonify
        result = UserService.toggle_status(user_id, data)
        
        # SỬA: Kiểm tra lỗi chuẩn
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)

        return jsonify(result), result.get("code", HttpCode.success)

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error