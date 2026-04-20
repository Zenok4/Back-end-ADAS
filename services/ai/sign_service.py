import grpc

from helper.decode_image import decode_image
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode

import proto.sign_pb2 as sign_pb2
import proto.sign_pb2_grpc as sign_pb2_grpc

from config import GRPC_SERVER_URL

class SignService:
    def __init__(self):
        self.channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = sign_pb2_grpc.SignServiceStub(self.channel)

    async def predict_sign(self, image_base64: str):
        try:
            # decode base64 -> bytes
            image_bytes = decode_image(image_base64)

            request = sign_pb2.SignRequest(
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

            meta = {
                "start_time": response.meta.start_time,
                "end_time": response.meta.end_time,
                "duration_ms": response.meta.duration_ms
            }

            data = {
                "detections": detections,
                "meta": meta
            }

            return response_success(
                data=data,
                key="data",
                message="Analyze sign success",
                code=HttpCode.success
            )

        except grpc.RpcError as e:
            return response_error(
                code=HttpCode.bad_request,
                message=f"gRPC error: {e.details()}"
            )