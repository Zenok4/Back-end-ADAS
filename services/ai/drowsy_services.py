# services/ai/drowsy_services.py
import requests
from datetime import datetime
from decimal import Decimal

from models.drowsiness_event import DrowsinessEvent
from database import db
from config import AI_SERVER_URL


class DrowsyService:
    def __init__(self):
        self.base = AI_SERVER_URL.rstrip("/")
        self.predict_url = f"{self.base}/drowsy/predict"

    def _to_confidence(self, is_drowsy: bool, ratio_eyes: float) -> Decimal:
        """
        Quy đổi đơn giản về [0,1] để khớp constraint của model.
        Bạn có thể thay bằng công thức chuẩn sau này.
        """
        # ví dụ: nếu buồn ngủ -> 0.9, ngược lại -> 0.1
        val = 0.9 if is_drowsy else 0.1
        return Decimal(str(round(val, 4)))

    def detect_drowsiness(self, image_data, detection_event_id: int | None = None):
        try:
            filename = getattr(image_data, "filename", None) or "upload.jpg"
            mimetype = (
                getattr(image_data, "mimetype", None) or "application/octet-stream"
            )
            stream = getattr(image_data, "stream", None) or image_data

            files = {"image": (filename, stream, mimetype)}
            resp = requests.post(self.predict_url, files=files, timeout=15)

            if resp.status_code != 200:
                raise Exception(f"AI server {resp.status_code}: {resp.text}")

            result = resp.json()
            is_drowsy = bool(result.get("is_drowsy", False))
            ratio_eyes = float(result.get("ratio_eyes", 0.0))
            message = result.get("message", "")
            frame_count = int(result.get("frame_count", 0) or 0)
            latency_ms = int(result.get("latency_ms", 0) or 0)

            # ====== GHI DB CHỈ KHI CÓ detection_event_id ======
            created_event_id = None
            if detection_event_id is not None:
                conf = self._to_confidence(is_drowsy, ratio_eyes)

                event = DrowsinessEvent(
                    detection_event_id=detection_event_id,
                    # tuỳ bạn có dữ liệu thật thì set, còn không để None/0:
                    eye_closure_duration_ms=None,  # hoặc tính từ frame_count -> ms nếu bạn có FPS
                    yawn_detected=False,
                    head_nod_count=0,
                    confidence=conf,
                    # created_at/updated_at tự set theo default của model
                )
                db.session.add(event)
                db.session.commit()
                created_event_id = event.id

            # Trả về theo schema BE đang dùng (không cần đúng cột DB)
            return {
                "is_drowsy": is_drowsy,
                "message": message,
                "eye_aspect_ratio": ratio_eyes,
                "frame_count": frame_count,
                "latency_ms": latency_ms,
                "drowsiness_event_id": created_event_id,  # None nếu không ghi DB
            }

        except Exception as e:
            raise Exception(f"Error in drowsy detection: {e}")
