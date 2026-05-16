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
        "confidence": lane_data.confidence,
        "class_id": lane_data.class_id,
        "class_name": lane_data.class_name,
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

            departure = response.lane_departure
            data = {
                "detections": detections,
                "lane_departure": {
                    "status": departure.status,
                    "message": departure.message,
                    "lane_offset": departure.lane_offset,
                    "left_lane": _lane_to_dict(departure.left_lane) if departure.HasField("left_lane") else None,
                    "right_lane": _lane_to_dict(departure.right_lane) if departure.HasField("right_lane") else None,
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
