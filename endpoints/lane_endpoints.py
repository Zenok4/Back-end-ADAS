from datetime import datetime
from flask import Blueprint, request, jsonify
from services.ai.lane_service import LaneService
from helper.normalization_response import response_error
from services.history.events_service import DetectTripService
from type.http_constants import HttpCode

lane_bp = Blueprint("lane", __name__)
lane_service = LaneService()

@lane_bp.route("/predict", methods=["POST"])
async def lane_predict():
    try:
        data = request.get_json()
        
        # Validate dữ liệu đầu vào
        if not data or "image_base64" not in data:
            return jsonify(response_error(
                message="No image_base64 provided",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        base64_img = data["image_base64"]

        user_id = data.get("user_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        captured_at = None
        if data.get("captured_at"):
            captured_at = datetime.fromisoformat(data["captured_at"])

        # Gọi service xử lý
        result = await lane_service.predict_lane(base64_img)

        # Kiểm tra nếu service trả về lỗi kết nối hoặc lỗi logic
        if isinstance(result, dict) and result.get("error"):
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_gateway
            )), HttpCode.bad_gateway
        
        DetectTripService.handle_detect_context(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            event_type="lane",
            payload=result.get("data"),
            captured_at=captured_at
        )

        # Trả về kết quả thành công
        return jsonify(result), HttpCode.success
        
    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error