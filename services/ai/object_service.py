import httpx
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode
from config import AI_SERVER_URL, async_client

class ObjectService:
    def __init__(self):
        # Giả định AI Server có endpoint tương tự sign
        self.ai_server_url = f"{AI_SERVER_URL.rstrip('/')}/object/predict"

    async def predict_object(self, image_base64: str):
        payload = {"image_base64": image_base64}
        try:
            # Gửi request sang AI Server (YOLO)
            resp = await async_client.post(self.ai_server_url, json=payload)
            
            if resp.status_code != 200:
                return response_error(code=HttpCode.bad_request, message="AI server returned error for Object")
            
            data = resp.json()

            return response_success(
                data=data,
                key="data",
                message="Analyze object success",
                code=HttpCode.success
            )
        except httpx.RequestError as e:
            return {"error": f"Failed to connect to AI server: {str(e)}", "url": self.ai_server_url}