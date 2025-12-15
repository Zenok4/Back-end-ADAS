# endpoints/drowsy_endpoints.py
from datetime import datetime
from flask import Blueprint, request
from services.ai.drowsy_services import DrowsyService
from middlewares.permission_required import permission_required
from helper.normalization_response import response_error, response_success
from services.history.events_service import DetectTripService
from type.http_constants import HttpCode

drowsy_bp= Blueprint("drowsy", __name__)
drowsy_service = DrowsyService()


@drowsy_bp.route("/detect", methods=["POST"])
async def detect_drowsiness():
    try:
        data = request.get_json(silent=True) or {}

        image_base64 = data.get("image_base64")
        session_id = data.get("session_id")
        if not image_base64:
            return response_error("Missing image_base64", HttpCode.bad_gateway)

        user_id = data.get("user_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        captured_at = None
        if data.get("captured_at"):
            captured_at = datetime.fromisoformat(data["captured_at"]) 

        # ---------- Gọi service ----------
        result = await drowsy_service.detect_drowsiness(
            image_base64=image_base64,
            session_id=session_id,
        )
        
        DetectTripService.handle_detect_context(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            event_type="drowsiness",
            payload=result,
            captured_at=captured_at
        )

        return response_success(data=result, message="Drowsiness detection successful", code=HttpCode.success)

    except Exception as e:
        return response_error(str(e), HttpCode.internal_server_error)