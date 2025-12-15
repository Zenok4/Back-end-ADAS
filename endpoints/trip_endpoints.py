from flask import Blueprint, request, jsonify
from datetime import datetime

from services.history.trip_service import TripHistoryService
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

trip_bp = Blueprint("trip", __name__)

@trip_bp.route("/", methods=["GET"])
def list_trips():
    """
    Lấy danh sách các chuyến đi của người dùng.
    
    - Method: GET
    - URL: /api/trips/
    - Query params:
        - user_id (int, required): ID người dùng
        - start_date (ISO datetime, optional): Thời gian bắt đầu lọc
        - end_date (ISO datetime, optional): Thời gian kết thúc lọc

    - Trả về:
        {
          success: true,
          message: string,
          code: int,
          data: [
            {
              date: "YYYY-MM-DD",
              car: { id, name, plate },
              duration_minutes: int,
              alerts: { total, drowsiness, object, lane, sign },
              events: [...]
            }
          ]
        }
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify(response_error(
                message="user_id is required",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)

        trips = TripHistoryService.list_trips(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        if not trips:
            return jsonify(response_success(
                code=HttpCode.success,
                message="No trips found"
            )), HttpCode.success

        return jsonify(response_success(
            code=HttpCode.success,
            data=trips,
            message="Trips retrieved successfully"
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error

@trip_bp.route("/location", methods=["POST"])
def record_location():
    """
    Ghi nhận vị trí (location) của người dùng trong chuyến đi.

    - Method: POST
    - URL: /api/trips/location
    - Input JSON:
        {
          "user_id": int,
          "latitude": float,
          "longitude": float,
          "captured_at": "ISO datetime" (optional)
        }

    - Trả về:
        {
          success: true,
          message: string,
          code: int,
          data: { "id": trip_id }
        }
    """
    try:
        data = request.get_json()

        required_fields = ["user_id", "latitude", "longitude"]
        if not data or not all(f in data for f in required_fields):
            return jsonify(response_error(
                message="Missing required fields",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        captured_at = None
        if data.get("captured_at"):
            captured_at = datetime.fromisoformat(data["captured_at"])

        trip = TripHistoryService.record_location(
            user_id=data["user_id"],
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            captured_at=captured_at
        )

        return jsonify(response_success(
            code=HttpCode.success,
            data={
                "id": trip.id
            },
            message="Location recorded successfully"
        )), HttpCode.success

    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error

@trip_bp.route("/summary", methods=["GET"])
def trip_summary():
    """
    Lấy thông tin tổng hợp chuyến đi của người dùng.

    - Method: GET
    - URL: /api/trips/summary
    - Query params:
        - user_id (int, required)

    - Trả về:
        {
          success: true,
          message: string,
          code: int,
          data: {
            latest_location: { latitude, longitude },
            car_name: string,
            total_time_seconds: int,
            total_alerts: int
          }
        }
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify(response_error(
                message="user_id is required",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        summary = TripHistoryService.get_summary(user_id)

        return jsonify(response_success(
            code=HttpCode.success,
            data=summary,
            message="Trip summary retrieved successfully"
        )), HttpCode.success


    except Exception as e:
        return jsonify(response_error(
            message=str(e),
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error

@trip_bp.route("/events-by-day", methods=["GET"])
def list_events_by_day():
    """
    Lấy danh sách sự kiện theo từng ngày, có phân trang và lọc.

    - Method: GET
    - URL: /api/trips/events-by-day
    - Query params:
        - user_id (int, required)
        - start_date (ISO datetime, optional)
        - end_date (ISO datetime, optional)
        - event_type (string: sign | drowsiness | object | lane, optional)
        - page (int, default=1)
        - page_size (int, default=100)

    - Trả về:
        {
          success: true,
          message: string,
          code: int,
          data: [
            {
              date: "YYYY-MM-DD",
              events: [...],
              summary: {...},
              page: int,
              page_size: int,
              total_items: int,
              total_pages: int
            }
          ]
        }
    """
    user_id = request.args.get("user_id", type=int)

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=100, type=int)
    event_type = request.args.get("event_type")

    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)

    data = TripHistoryService.list_events_by_day(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        event_type=event_type,
        page=page,
        page_size=page_size
    )

    if not data:
        return jsonify(response_error(
            message="No trips found",
            code=HttpCode.success
        )), HttpCode.success

    return jsonify(response_success(
        data=data,
        message="Trip events by day retrieved successfully",
        code=HttpCode.success,
    )), HttpCode.success