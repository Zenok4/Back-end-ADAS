import requests
from config import AI_SERVER_URL
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode


class SignService:
    def __init__(self):
        # Đọc từ config và in ra để debug
        print(f"AI Server URL from config: {AI_SERVER_URL}")
        self.ai_server_url = f"{AI_SERVER_URL}/sign/predict"  # Thường AI server có prefix /api
        print(f"Full AI endpoint URL: {self.ai_server_url}")

    def predict_sign(self, image_base64: str):
        # Payload gửi sang AI server
        payload = {"image_base64": image_base64}

        try:
            response = requests.post(self.ai_server_url, json=payload, timeout=30)

            if not response.ok:
                return response_error(
                    code=response.status_code,
                    message="Error from AI server",
                )

            return response_success(
                data=response.json(),
                key="data",
                message="Analyze sign success",
                code=HttpCode.success
            )

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to connect to AI server: {str(e)}",
                "url": self.ai_server_url
            }
