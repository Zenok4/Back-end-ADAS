from flask import Blueprint, request, jsonify
from services.ai.sign_service import SignService
from helper.normalization_response import response_error
from type.http_constants import HttpCode

sign_bp = Blueprint("sign", __name__)
sign_service = SignService()

@sign_bp.route("/predict", methods=["POST"])
def sign_predict():
    try:
        data = request.get_json()
        if not data or "image_base64" not in data:
            return jsonify(response_error(
                message="No image_base64 provided",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        base64_img = data["image_base64"]
        result = sign_service.predict_sign(base64_img)

        # Nếu service trả lỗi
        if isinstance(result, dict) and result.get("error"):
            return jsonify(result), HttpCode.bad_gateway

        # Trả trực tiếp mảng detections
        # response_success trả ra dict kiểu: {"code":..., "message":..., "data": [...]}
        # frontend chỉ cần res.data để lấy mảng
        return jsonify(result), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error
