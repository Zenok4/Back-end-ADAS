import grpc
from helper.normalization_response import response_success, response_error
from helper.decode_image import decode_image
from type.http_constants import HttpCode

import proto.lane_pb2 as lane_pb2
import proto.lane_pb2_grpc as lane_pb2_grpc

from config import GRPC_SERVER_URL


class LaneService:
    def __init__(self):
        self.channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = lane_pb2_grpc.LaneServiceStub(self.channel)

    async def predict_lane(self, image_base64: str):
        try:
            # decode
            image_bytes = decode_image(image_base64)

            request = lane_pb2.LaneRequest(
                image=image_bytes
            )

            response = self.stub.Predict(request)

            detections = []

            for d in response.detections:
                detections.append({
                    "box": list(d.box),
                    "confidence": d.confidence,
                    "class_id": d.class_id,
                    "class_name": d.class_name
                })

            data = {
                "detections": detections,
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