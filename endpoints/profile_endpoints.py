from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.authen.user_service import UserService
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

# Tạo blueprint mới cho profile, khớp với ApiUrls.profile.update
profile_bp = Blueprint("profile_bp", __name__, url_prefix="/profile")


@profile_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_my_profile():
    """
    API: Cập nhật profile cho user đang đăng nhập.
    - Endpoint: PUT /profile/update
    - Lấy user_id từ JWT token.
    - Frontend: profileService.ts -> updateProfile()
    """
    try:
        # 1. Lấy user_id từ token JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(response_error("Invalid token", HttpCode.unauthorized)), HttpCode.unauthorized

        # 2. Lấy data từ JSON payload
        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify(response_error("Missing JSON payload", HttpCode.bad_request)), HttpCode.bad_request
        
        # 3. Lọc ra các trường mà frontend gửi (khớp với ProfileUpdatePayload)
        payload = {
            "email": data.get("email"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "vehicle_name": data.get("vehicle_name"),
            "license_plate": data.get("license_plate")
        }
        
        # 4. Gọi hàm update_user (đã được sửa ở bước 1)
        result = UserService.update_user(user_id, payload)
        
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
        
        # 5. Trả về thông tin user đã cập nhật
        # Frontend (profileService) mong đợi { message, data }
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