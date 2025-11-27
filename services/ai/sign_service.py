import httpx
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode
from config import AI_SERVER_URL, async_client

class SignService:
    def __init__(self):
        self.ai_server_url = f"{AI_SERVER_URL.rstrip('/')}/sign/predict"

    async def predict_sign(self, image_base64: str):
        payload = {"image_base64": image_base64}
        try:
            resp = await async_client.post(self.ai_server_url, json=payload)
            if resp.status_code != 200:
                return response_error(code=HttpCode.bad_request, message="AI server returned error")
            
            data = resp.json()

            return response_success(
                data=data,
                key="data",
                message="Analyze sign success",
                code=HttpCode.success
            )
        except httpx.RequestError as e:
            return {"error": f"Failed to connect to AI server: {str(e)}", "url": self.ai_server_url}
