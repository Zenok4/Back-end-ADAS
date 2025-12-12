import httpx
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode
from config import AI_SERVER_URL, async_client

class LaneService:
    def __init__(self):
        # Trỏ đúng vào endpoint /lane/predict bên AI Server
        self.ai_server_url = f"{AI_SERVER_URL.rstrip('/')}/lane/predict"

    async def predict_lane(self, image_base64: str):
        """
        Gửi ảnh Base64 sang AI Server để nhận diện làn đường.
        """
        # Payload khớp với yêu cầu của AI Server
        payload = {"image_base64": image_base64}
        
        try:
            # Gọi Async request sang AI Server (Timeout mặc định của httpx có thể cần tăng nếu mạng chậm)
            resp = await async_client.post(self.ai_server_url, json=payload, timeout=10.0)
            
            if resp.status_code != 200:
                # Log lỗi nếu cần thiết
                return response_error(code=HttpCode.bad_request, message=f"AI server returned error: {resp.text}")
            
            data = resp.json()

            # Trả về kết quả chuẩn hóa
            return response_success(
                data=data,
                key="data",
                message="Analyze lane success",
                code=HttpCode.success
            )
        except httpx.RequestError as e:
            return {"error": f"Failed to connect to AI server: {str(e)}", "url": self.ai_server_url}
        except Exception as e:
            return {"error": f"Internal error during prediction: {str(e)}"}