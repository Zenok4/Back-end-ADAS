# endpoints/drowsy_endpoints.py
from flask import Blueprint, request
from services.ai.drowsy_services import DrowsyService
from middlewares.permission_required import permission_required
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

drowsy_bp= Blueprint("drowsy", __name__)
drowsy_service = DrowsyService()


@drowsy_bp.route("/detect", methods=["POST"])
def detect_drowsiness():
    try:
        data = request.get_json(silent=True) or {}

        image_base64 = data.get("image_base64")
        session_id = data.get("session_id")
        if not image_base64:
            return response_error("Missing image_base64", HttpCode.bad_gateway)

         # ---------- detection_event_id (optional) ----------
        deid = data.get("detection_event_id")
        detection_event_id = int(deid) if deid not in (None, "") else None

        # ---------- Gọi service ----------
        result = drowsy_service.detect_drowsiness(
            image_base64=image_base64,
            session_id=session_id,
            detection_event_id=detection_event_id,
        )

        return response_success(result)

    except Exception as e:
        return response_error(str(e), HttpCode.internal_server_error)