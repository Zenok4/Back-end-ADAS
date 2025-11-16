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
        payload = {"image_base64": image_base64}

        try:
            response = requests.post(self.ai_server_url, json=payload, timeout=30)

            if not response.ok:
                return {
                    "error": "Error from AI server",
                    "code": response.status_code
                }

            ai_res = response.json()
            return ai_res.get("data", [])

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to connect to AI server: {str(e)}",
                "url": self.ai_server_url
            }
