from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.authen.user_service import UserService
from type.http_constants import HttpCode
from helper.normalization_response import response_error
from helper.check_constraints_roles import get_current_user_highest_level

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

# ================== LIST ==================
@user_bp.route("/list", methods=["GET"])
@jwt_required()
def list_users():
    """
    Lấy danh sách người dùng (có phân trang + lọc).
    - Query params:
        - page: số trang (mặc định 1)
        - limit: số dòng mỗi trang (mặc định 20)
        - search: từ khóa tìm kiếm (username/email/phone)
        - is_active: 'true' hoặc 'false' (lọc theo trạng thái)
        - role_id: ID của role (lọc theo vai trò)
    - Trả về:
        { success, message, code, data: { users, page, limit, total } }
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        
        search = request.args.get("search", None)
        is_active_str = request.args.get("is_active", None)
        role_id = request.args.get("role_id", None, type=int)

        is_active = None
        if is_active_str == 'true':
            is_active = True
        elif is_active_str == 'false':
            is_active = False

        result = UserService.get_all_users(
            page=page, 
            limit=limit, 
            search=search, 
            is_active=is_active, 
            role_id=role_id
        )
        
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== DETAIL BY ID ==================
@user_bp.route("/id/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_detail(user_id):
    """
    Lấy thông tin chi tiết người dùng theo ID.
    - Query params:
        - include_roles: true/false (mặc định false)
    - Trả về:
        { success, message, code, data: { user info } }
    """
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"
    result = UserService.get_user_by_id(user_id, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== DETAIL BY USERNAME ==================
@user_bp.route("/username/<string:username>", methods=["GET"])
@jwt_required()
def get_user_by_username(username):
    """
    Lấy thông tin người dùng theo username.
    - Query params:
        - include_roles: true/false (mặc định false)
    - Trả về:
        { success, message, code, data: { user info } }
    """
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"
    result = UserService.get_user_by_username(username, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== FILTER BY ACTIVE STATUS ==================
@user_bp.route("/active/<string:is_active>", methods=["GET"])
@jwt_required()
def list_users_by_active(is_active):
    """
    Lọc danh sách người dùng theo trạng thái hoạt động.
    - Path param:
        - is_active: "true" hoặc "false"
    - Query params:
        - include_roles: true/false
    - Trả về:
        { success, message, code, data: { users } }
    """
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"
    is_active_bool = is_active.lower() == "true"
    result = UserService.get_users_by_active(is_active_bool, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== CREATE ==================
@user_bp.route("/create", methods=["POST"])
@jwt_required()
def create_user():
    """
    Tạo mới một người dùng.
    - Input JSON:
        {
            "username": "...",
            "email": "...",
            "phone": "...",
            "password": "...",
            "display_name": "..." (optional)
        }
    - Trả về:
        { success, message, code, data: { user info } }
    """
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.create_user(data)
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
@jwt_required()
def update_user(user_id):
    """
    Cập nhật thông tin người dùng.
    - Input JSON (có thể cập nhật 1 hoặc nhiều trường):
        {
            "username": "...",
            "email": "...",
            "phone": "...",
            "display_name": "..."
        }
    - Trả về:
        { success, message, code, data: { user info } }
    """
    data = request.get_json(silent=True) or {}
    try:
        # QUAN TRỌNG: Lấy level hiện tại để kiểm tra quyền sửa đổi
        current_level = get_current_user_highest_level()
        
        result = UserService.update_user(user_id, data, current_user_level=current_level)
        
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
@jwt_required()
def delete_user(user_id):
    """
    Xóa một người dùng theo ID.
    - Path param:
        - user_id
    - Trả về:
        { success, message, code, data: { id } }
    """
    try:
        # QUAN TRỌNG: Lấy level hiện tại để kiểm tra quyền xóa
        current_level = get_current_user_highest_level()
        
        result = UserService.delete_user(user_id, current_user_level=current_level)
        
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
@jwt_required()
def toggle_user_status(user_id):
    """
    Thay đổi trạng thái hoạt động của người dùng (active / inactive).
    - Input JSON:
        {
            "is_active": true/false
        }
    - Trả về:
        { success, message, code, data: { user info } }
    """
    data = request.get_json(silent=True) or {}
    try:
        current_level = get_current_user_highest_level()
        result = UserService.toggle_status(user_id, data, current_user_level=current_level)
        
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== SEND OTP FOR CHANGE PASSWORD (MỚI) ==================
@user_bp.route("/change-password/send-otp", methods=["POST"])
@jwt_required()
def send_otp_change_password():
    """
    Input JSON: { "channel": "email" } hoặc { "channel": "phone" }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        channel = data.get("channel", "email") # Mặc định là email

        result = UserService.send_otp_for_change_password(int(current_user_id), channel)
        
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error

# ================== CHANGE PASSWORD (CÓ OTP) ==================
@user_bp.route("/change-password/<int:user_id>", methods=["PATCH"])
@jwt_required()
def change_password(user_id):
    """
    Đổi mật khẩu của người dùng (yêu cầu OTP).
    - Input JSON: 
        { 
            "old_password": "...", 
            "new_password": "...",
            "otp_code": "..." 
        }
    """
    # 1. BẢO MẬT: Kiểm tra người gọi API có phải là chính chủ không
    current_user_id = get_jwt_identity()
    if int(current_user_id) != user_id:
         return jsonify(response_error("Unauthorized action: You can only change your own password", code=HttpCode.forbidden)), HttpCode.forbidden

    data = request.get_json(silent=True) or {}
    try:
        # Gọi Service Change Password (đã cập nhật logic check OTP)
        result = UserService.change_password(user_id, data)
        
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
            
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error