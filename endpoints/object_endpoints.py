from flask import Blueprint, request, jsonify
from services.ai.object_service import ObjectService
from helper.normalization_response import response_error
from type.http_constants import HttpCode

object_bp = Blueprint("object", __name__)
object_service = ObjectService()

@object_bp.route("/predict", methods=["POST"])
async def object_predict():
    try:
        data = request.get_json()
        if not data or "image_base64" not in data:
            return jsonify(response_error(
                message="No image_base64 provided",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        base64_img = data["image_base64"]

        # Gọi service
        result = await object_service.predict_object(base64_img)

        # Kiểm tra lỗi
        if isinstance(result, dict) and result.get("error"):
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_gateway
            )), HttpCode.bad_gateway

        # Trả về kết quả
        return jsonify({
            "code": HttpCode.success,
            "data": result
        }), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error