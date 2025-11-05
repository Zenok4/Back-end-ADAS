# endpoints/drowsy_endpoints.py
from flask import Blueprint, request
from services.ai.drowsy_services import DrowsyService
from middlewares.permission_required import permission_required
from helper.normalization_response import response_error, response_success

drowsy_blueprint = Blueprint("drowsy", __name__)
drowsy_service = DrowsyService()


@drowsy_blueprint.route("/detect", methods=["POST"])
def detect_drowsiness():
    try:
        image_data = request.files.get("image")
        if not image_data:
            return response_error("No image provided", 400)

        # lấy detection_event_id nếu FE muốn lưu DB
        deid = request.form.get("detection_event_id") or request.args.get(
            "detection_event_id"
        )
        detection_event_id = int(deid) if deid is not None and deid != "" else None

        result = drowsy_service.detect_drowsiness(image_data, detection_event_id)
        return response_success(result)

    except Exception as e:
        return response_error(str(e), 500)
