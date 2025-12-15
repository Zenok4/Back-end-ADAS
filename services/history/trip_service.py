from collections import defaultdict
from datetime import datetime
from sqlalchemy import desc, func, cast, Date, case

from database import db
from helper.cal_avg_conf import _calc_avg_confidence
from models.sign_detection import SignDetection
from models.trip_history import TripHistory
from models.detection_event import DetectionEvent
from models.car import Car

class TripHistoryService:

    @staticmethod
    def list_trips(user_id, start_date=None, end_date=None):
        trip_date = cast(TripHistory.captured_at, Date).label("trip_date")

        base_query = (
            db.session.query(
                trip_date,
                TripHistory.car_id,
                func.min(TripHistory.captured_at).label("start_time"),
                func.max(TripHistory.captured_at).label("end_time"),
                func.count().label("points")
            )
            .filter(TripHistory.user_id == user_id)
            .group_by(trip_date, TripHistory.car_id)
            .order_by(desc(trip_date))
        )

        if start_date:
            base_query = base_query.filter(TripHistory.captured_at >= start_date)
        if end_date:
            base_query = base_query.filter(TripHistory.captured_at <= end_date)

        trips = base_query.all()
        results = []

        for trip in trips:
            alerts = TripHistoryService._count_events_fast(
                user_id,
                trip.start_time,
                trip.end_time
            )

            events = TripHistoryService.list_trip_events(
                user_id,
                trip.start_time,
                trip.end_time
            )

            car = Car.query.get(trip.car_id)

            results.append({
                "date": trip.trip_date.isoformat(),
                "car": {
                    "id": car.id,
                    "name": car.name,
                    "plate": car.plate_number
                },
                "duration_minutes": int(
                    (trip.end_time - trip.start_time).total_seconds() / 60
                ),
                "alerts": alerts,
                "events": events
            })

        return results
    
    @staticmethod
    def list_trip_events(user_id, start_time, end_time):
        events = (
            DetectionEvent.query
            .filter(
                DetectionEvent.user_id == user_id,
                DetectionEvent.event_time.between(start_time, end_time)
            )
            .order_by(DetectionEvent.event_time.asc())
            .all()
        )

        results = []

        for e in events:

            if isinstance(e.payload, dict):
                avg_confidence = _calc_avg_confidence(e.payload)

            results.append({
                "id": e.id,
                "detect_type": e.event_type,
                "time": e.event_time.isoformat(),
                "avg_confidence": avg_confidence,
                "payload": e.payload
            })

        return results

    @staticmethod
    def list_events_by_day(user_id, start_date=None, event_type=None, end_date=None, page=1, page_size=100):
        query = (
            db.session.query(DetectionEvent)
            .filter(DetectionEvent.user_id == user_id)
        )

        if event_type:
            query = query.filter(DetectionEvent.event_type == event_type)

        total_items = query.count()

        if start_date:
            query = query.filter(DetectionEvent.event_time >= start_date)
        if end_date:
            query = query.filter(DetectionEvent.event_time <= end_date)

        events = (
            query
            .order_by(DetectionEvent.event_time.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        grouped = defaultdict(lambda: {
            "events": [],
            "summary": defaultdict(lambda: {
                "total_events": 0,
                "total_detections": 0,
                "conf_sum": 0.0,
            })
        })

        for e in events:
            day = e.event_time.date().isoformat()
            event_type = e.event_type

            avg_conf = None
            count = 0
            conf_sum = 0.0
            total_drowsiness_detections = 0

            if e.event_type == "sign":
                data = e.payload.get("data", []) if e.payload else []

                confidences = [
                    float(d["confidence"])
                    for d in data
                    if isinstance(d, dict)
                    and isinstance(d.get("confidence"), (int, float))
                    and d["confidence"] >= 0
                ]

                count = len(confidences)

                if count > 0:
                    conf_sum = sum(confidences)
                    avg_conf = round(conf_sum / count, 4)
                else:
                    conf_sum = 0.0
                    avg_conf = None

            elif e.event_type == "drowsiness":
                if e.payload and "is_drowsy" in e.payload:
                    count = 1
                    print("Processing drowsiness event payload:", e.payload)
                    total_drowsiness_detections = 1 if e.payload.get("is_drowsy") == True else 0

            elif e.event_type == "object":
                data = e.payload.get("data", []) if e.payload else []

                confidences = [
                    float(d["confidence"])
                    for d in data
                    if isinstance(d, dict)
                    and isinstance(d.get("confidence"), (int, float))
                    and d["confidence"] >= 0
                ]

                count = len(confidences)

                if count > 0:
                    conf_sum = sum(confidences)
                    avg_conf = round(conf_sum / count, 4)
                else:
                    conf_sum = 0.0
                    avg_conf = None

            elif e.event_type == "lane":
                data = e.payload.get("data", []) if e.payload else []

                confidences = [
                    float(d["confidence"])
                    for d in data
                    if isinstance(d, dict)
                    and isinstance(d.get("confidence"), (int, float))
                    and d["confidence"] >= 0
                ]

                count = len(confidences)

                if count > 0:
                    conf_sum = sum(confidences)
                    avg_conf = round(conf_sum / count, 4)
                else:
                    conf_sum = 0.0
                    avg_conf = None


            # 1️⃣ giữ event con (KHÔNG ĐỔI)
            grouped[day]["events"].append({
                "id": e.id,
                "type": event_type,
                "time": e.event_time.isoformat(),
                "avg_confidence": avg_conf,
                "count": count,
                "payload": e.payload,
                "total drownsiness detections": total_drowsiness_detections
            })

            summary = grouped[day]["summary"][event_type]
            summary["total_events"] += 1
            summary["total_detections"] += count
            summary["conf_sum"] += conf_sum
            summary["total_drowsiness_detections"] = summary.get("total_drowsiness_detections", 0) + total_drowsiness_detections
            
        result = []

        for day, data in grouped.items():
            summary_out = {}

            for event_type, s in data["summary"].items():
                avg_conf = (
                    round(s["conf_sum"] / s["total_detections"], 4)
                    if s["total_detections"] > 0
                    else None
                )

                is_drowsiness = event_type == "drowsiness"

                print("Processing summary for", event_type, "is_drowsiness:", is_drowsiness)

                summary_out[event_type] = {
                    "total_events": s["total_events"],
                    "total_detections": s["total_detections"],
                    **({"avg_confidence": avg_conf} if not is_drowsiness else {}),
                    **({"total_drowsiness_detections": s["total_drowsiness_detections"]} if is_drowsiness else {})
                }

            result.append({
                "date": day,
                "events": data["events"],
                "summary": summary_out,
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": (total_items + page_size - 1) // page_size
            })

        return result


    @staticmethod
    def _count_events_fast(user_id, start, end):
        """
        1 query duy nhất cho tất cả loại event
        """

        rows = (
            db.session.query(
                DetectionEvent.event_type,
                func.count().label("count")
            )
            .filter(
                DetectionEvent.user_id == user_id,
                DetectionEvent.event_time.between(start, end)
            )
            .group_by(DetectionEvent.event_type)
            .all()
        )

        result = {
            "total": 0,
            "drowsiness": 0,
            "object": 0,
            "lane": 0,
            "sign": 0
        }

        for r in rows:
            result["total"] += r.count

            if r.event_type == "drowsiness":
                result["drowsiness"] = r.count
            elif r.event_type == "object":
                result["object"] = r.count
            elif r.event_type == "lane":
                result["lane"] = r.count
            elif r.event_type == "sign":
                result["sign"] = r.count

        return result
    
    @staticmethod
    def get_summary(user_id):
        latest = (
            TripHistory.query
            .filter_by(user_id=user_id)
            .order_by(TripHistory.captured_at.desc())
            .first()
        )

        time_range = (
            db.session.query(
                func.min(TripHistory.captured_at),
                func.max(TripHistory.captured_at)
            )
            .filter(TripHistory.user_id == user_id)
            .first()
        )

        total_alerts = (
            DetectionEvent.query
            .filter(DetectionEvent.user_id == user_id)
            .count()
        )

        total_seconds = 0
        if time_range and time_range[0] and time_range[1]:
            total_seconds = int(
                (time_range[1] - time_range[0]).total_seconds()
            )

        return {
            "latest_location": {
                "latitude": float(latest.latitude) if latest else None,
                "longitude": float(latest.longitude) if latest else None,
            },
            "car_name": latest.car.name if latest and latest.car else None,
            "total_time_seconds": total_seconds,
            "total_alerts": total_alerts
        }
    
    @staticmethod
    def record_location(
        user_id: int,
        latitude: float,
        longitude: float,
        captured_at: datetime
    ):
        car = Car.query.filter_by(user_id=user_id).first()
        if not car:
            return None
        
        trip = TripHistory(
            user_id=user_id,
            car_id=car.id or None,
            latitude=latitude,
            longitude=longitude,
            captured_at=captured_at or datetime.now()
        )

        db.session.add(trip)
        return trip
