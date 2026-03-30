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
        data = request.get_json(silent=True) or {}
        if "image_base64" not in data:
            return jsonify(response_error(
                message="No image_base64 provided",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        base64_img = data.get("image_base64")
        session_id = data.get("session_id")
        ego_state = data.get("ego_state") or {}
        camera = data.get("camera") or {}

        user_id = data.get("user_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        captured_at = None
        if data.get("captured_at"):
            captured_at = datetime.fromisoformat(data["captured_at"])

        result = await object_service.predict_object(
            image_base64=base64_img,
            session_id=session_id,
            ego_state=ego_state,
            camera=camera,
        )

        if isinstance(result, dict) and result.get("error"):
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_gateway
            )), HttpCode.bad_gateway

        DetectTripService.handle_detect_context(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            event_type="object",
            payload=result.get("data"),
            captured_at=captured_at
        )

        return jsonify(result), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error
