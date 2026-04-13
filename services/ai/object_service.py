import grpc

from helper.decode_image import decode_image
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode

import proto.object_pb2 as object_pb2
import proto.object_pb2_grpc as object_pb2_grpc

from config import GRPC_SERVER_URL

class ObjectService:
    def __init__(self):
        self.channel = grpc.insecure_channel(GRPC_SERVER_URL)
        self.stub = object_pb2_grpc.ObjectServiceStub(self.channel)

    async def predict_object(self, image_base64: str):
        try:
            # ✅ decode base64 -> bytes
            image_bytes = decode_image(image_base64)

            # ✅ build request
            request = object_pb2.DetectRequest(
                image=image_bytes
            )

            response = self.stub.Detect(request)

            objects = []

            for obj in response.objects:
                objects.append({
                    "id": obj.id,
                    "label": obj.label,
                    "confidence": obj.confidence,
                    "bbox": list(obj.bbox),
                    "speed": obj.speed
                })

            data = {
                "objects": objects,
                "processing_time": response.processing_time
            }

            return response_success(
                data=data,
                key="data",
                message="Analyze object success",
                code=HttpCode.success
            )

        except grpc.RpcError as e:
            return response_error(
                code=HttpCode.bad_request,
                message=f"gRPC error: {e.details()}"
            )