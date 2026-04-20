from datetime import datetime
from flask import Blueprint, request, jsonify
from services.ai.object_service import ObjectService
from helper.normalization_response import response_error
from services.history.events_service import DetectTripService
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

        user_id = data.get("user_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # =========================
        # 🔥 HANDLE TIME
        # =========================
        if data.get("captured_at"):
            captured_at_dt = datetime.fromisoformat(data["captured_at"])
        else:
            captured_at_dt = datetime.utcnow()

        # Captered_at for AI
        captured_at_ts = captured_at_dt.timestamp()

        print("Capture At (ts):", captured_at_ts)
        print("Capture At (dt):", captured_at_dt)

        # =========================
        # CALL AI
        # =========================
        result = await object_service.predict_object(
            base64_img,
            latitude,
            longitude,
            captured_at_ts  # ✅ float
        )

        # Handle error from gRPC
        if isinstance(result, dict) and result.get("error"):
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_gateway
            )), HttpCode.bad_gateway

        # =========================
        # SAVE DB
        # =========================
        DetectTripService.handle_detect_context(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            event_type="object",
            payload=result.get("data"),
            captured_at=captured_at_dt  # ✅ datetime
        )

        return jsonify({
            "code": HttpCode.success,
            "data": result
        }), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error