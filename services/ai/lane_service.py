import grpc
from helper.normalization_response import response_success, response_error
from helper.decode_image import decode_image
from type.http_constants import HttpCode

import proto.lane_pb2 as lane_pb2
import proto.lane_pb2_grpc as lane_pb2_grpc

from config import GRPC_SERVER_URL


def _lane_to_dict(lane_data):
    if lane_data is None:
        return None
    return {
        "box": list(lane_data.box),
        "line": list(lane_data.line),
        "confidence": lane_data.confidence,
        "class_id": lane_data.class_id,
        "class_name": lane_data.class_name,
    }


def _boundary_to_dict(boundary):
    if boundary is None or not boundary.class_name:
        return None
    return {
        "class_name": boundary.class_name,
        "line": list(boundary.line),
        "confidence": boundary.confidence,
        "x_at_reference": boundary.x_at_reference,
    }


def _current_lane_to_dict(current_lane):
    return {
        "available": current_lane.available,
        "status": current_lane.status,
        "message": current_lane.message,
        "reference_y": current_lane.reference_y,
        "vehicle_center_x": current_lane.vehicle_center_x,
        "lane_center_x": current_lane.lane_center_x,
        "lane_width_px": current_lane.lane_width_px,
        "offset_px": current_lane.offset_px,
        "offset_ratio": current_lane.offset_ratio,
        "warning": current_lane.warning,
        "warning_direction": current_lane.warning_direction,
        "warning_level": current_lane.warning_level,
        "left_boundary": _boundary_to_dict(current_lane.left_boundary),
        "right_boundary": _boundary_to_dict(current_lane.right_boundary),
    }


class LaneService:
    def __init__(self):
        self.channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = lane_pb2_grpc.LaneServiceStub(self.channel)

    async def predict_lane(self, image_base64: str):
        try:
            image_bytes = decode_image(image_base64)

            request = lane_pb2.LaneRequest(
                image=image_bytes
            )

            response = self.stub.Predict(request)

            detections = []
            for d in response.detections:
                detections.append(_lane_to_dict(d))

            current_lane = response.current_lane
            current_lane_data = _current_lane_to_dict(current_lane)
            data = {
                "detections": detections,
                "current_lane": current_lane_data,
                "lane_departure": {
                    "status": current_lane.status,
                    "message": current_lane.message,
                    "lane_offset": current_lane.offset_ratio,
                    "warning": current_lane.warning,
                    "warning_direction": current_lane.warning_direction,
                    "warning_level": current_lane.warning_level,
                    "left_lane": _boundary_to_dict(current_lane.left_boundary),
                    "right_lane": _boundary_to_dict(current_lane.right_boundary),
                },
                "meta": {
                    "processing_time": response.meta.processing_time
                }
            }

            return response_success(
                data=data,
                key="data",
                message="Analyze lane success",
                code=HttpCode.success
            )

        except grpc.RpcError as e:
            return response_error(
                code=HttpCode.bad_request,
                message=f"gRPC error: {e.details()}"
            )
