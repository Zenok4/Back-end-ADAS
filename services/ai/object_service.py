import httpx
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode
from config import AI_SERVER_URL, async_client

class ObjectService:
    def __init__(self):
        # Đảm bảo URL trỏ đúng vào router /object/predict bên AI
        self.ai_server_url = f"{AI_SERVER_URL.rstrip('/')}/object/predict"

    async def predict_object(self, image_base64: str):
        payload = {"image_base64": image_base64}
        try:
            resp = await async_client.post(self.ai_server_url, json=payload, timeout=5.0)
            
            if resp.status_code != 200:
                # Nếu lỗi thì báo lỗi, nhưng vẫn giữ format an toàn
                return response_error(code=HttpCode.bad_request, message="AI server returned error")
            
            # AI trả về: { "data": [...], "processing_time": ... }
            data = resp.json()

            # Bọc lại bằng response_success giống hệt SignService
            return response_success(
                data=data,
                key="data", # Key này quan trọng để Frontend lấy đúng data.data
                message="Analyze object success",
                code=HttpCode.success
            )
        except httpx.RequestError as e:
            return {"error": f"Failed to connect to AI server: {str(e)}", "url": self.ai_server_url}