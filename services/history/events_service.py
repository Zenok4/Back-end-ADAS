from datetime import datetime
from typing import Optional

from database import db

from models.detection_event import DetectionEvent
from models.drowsiness_event import DrowsinessEvents
from models.sign_detection import SignDetection
from models.lane_event import LaneEvent
from models.object_detection import ObjectDetection

from services.history.trip_service import TripHistoryService


class DetectTripService:

    @staticmethod
    def _resolve_event_severity(event_type: str, payload: dict | None) -> str:
        if not payload:
            return "warning"

        if event_type == "object":
            summary = payload.get("collision_summary") or {}
            highest = summary.get("highest_severity")
            if highest in ("safe", "low", "medium", "high", "critical"):
                return highest

        return "warning"

    @staticmethod
    def handle_detect_context(
        *,
        user_id: Optional[int],
        latitude: Optional[float],
        longitude: Optional[float],
        event_type: str,
        payload: dict | None,
        captured_at: datetime | None = None
    ):

        if user_id is None or latitude is None or longitude is None:
            return

        captured_at = captured_at or datetime.now()

        try:

            # Detection event (BẮT BUỘC severity)
            severity = DetectTripService._resolve_event_severity(event_type, payload)
            event = DetectionEvent(
                user_id=user_id,
                event_type=event_type,
                severity=severity,
                event_time=captured_at,
                payload=payload
            )
            db.session.add(event)
            db.session.flush()  # lấy event.id

            # Trip history
            TripHistoryService.record_location(
                user_id=user_id,
                latitude=float(latitude),
                longitude=float(longitude),
                captured_at=captured_at
            )

            # Sign detections
            if event_type == "sign" and payload:
                for det in payload.get("data", []):
                    if det.get("class_name") and det.get("confidence") is not None:
                        db.session.add(SignDetection(
                            detection_event_id=event.id,
                            sign_type=det.get("class_name"),
                            confidence=det.get("confidence")
                        ))

            elif event_type == "drowsiness" and payload:
                db.session.add(DrowsinessEvents(
                    detection_event_id=event.id,
                    is_drowsy=bool(payload.get("is_drowsy")),
                    eye_aspect_ratio=payload.get("eye_aspect_ratio"),
                ))

            elif event_type == "object" and payload:

                for det in payload.get("data", []):
                    if det.get("class_name") and det.get("confidence") is not None:
                        db.session.add(ObjectDetection(
                            detection_event_id=event.id,
                            object_type=det.get("class_name"),
                            confidence=det.get("confidence")
                        ))

            elif event_type == "lane" and payload:
                for det in payload.get("data", []):
                    if det.get("confidence") is not None:
                        db.session.add(LaneEvent(
                            detection_event_id=event.id,
                            confidence=det.get("confidence")
                        ))

        
            # COMMIT DUY NHẤT
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("DetectTripService failed:", e)
