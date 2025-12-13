from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.authen.user_service import UserService
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

profile_bp = Blueprint("profile_bp", __name__, url_prefix="/profile")

@profile_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_my_profile():
    """
    API: Cập nhật profile cho user đang đăng nhập.
    - Endpoint: PUT /profile/update
    - Lấy user_id từ JWT token.
    """
    try:
        # 1. Lấy user_id từ token JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(response_error("Invalid token", HttpCode.unauthorized)), HttpCode.unauthorized

        # 2. Lấy data từ JSON payload
        raw_data = request.get_json(silent=True) or {}
        if not raw_data:
            return jsonify(response_error("Missing JSON payload", HttpCode.bad_request)), HttpCode.bad_request
        
        # 3. Lọc dữ liệu: Chỉ lấy các trường được phép VÀ có tồn tại trong request gửi lên
        allowed_keys = [
            "email", "phone", "display_name", 
            "address", "vehicle_name", "license_plate"
        ]
        
        payload = {}
        for key in allowed_keys:
            # Chỉ thêm vào payload nếu key đó có trong dữ liệu gửi lên
            # Điều này tránh việc ghi đè giá trị None vào các trường không muốn sửa
            if key in raw_data:
                payload[key] = raw_data[key]

        if not payload:
             return jsonify(response_error("No valid fields to update", HttpCode.bad_request)), HttpCode.bad_request
        
        # 4. Gọi hàm update_user với cờ is_self_update=True
        result = UserService.update_user(user_id, payload, is_self_update=True)
        
        if not result.get("success"):
            # Trả về đúng code lỗi từ service (thường là 400 nếu trùng email/phone)
            return jsonify(result), result.get("code", HttpCode.bad_request)
        
        # 5. Trả về kết quả
        return jsonify(response_success(
            data=result.get("data"), 
            message="Profile updated successfully", 
            code=HttpCode.success
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error