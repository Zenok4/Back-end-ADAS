import requests
from config import AI_SERVER_URL
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode

class SignService:
    def __init__(self):
        self.ai_server_url = f"{AI_SERVER_URL}/sign/predict"

    def predict_sign(self, image_base64: str):
        payload = {"image_base64": image_base64}

        try:
            response = requests.post(self.ai_server_url, json=payload, timeout=30)

            if not response.ok:
                # Dùng response_error khi AI server lỗi
                return response_error(
                    message=f"Error from AI server: {response.status_code}",
                    code=HttpCode.bad_gateway
                )

            # AI server trả {"data": [...]}, chỉ lấy mảng detections
            data = response.json().get("data", [])
            return response_success(
                data=data,
                message="Analyze sign success",
                code=HttpCode.success
            )

        except requests.exceptions.RequestException as e:
            return response_error(
                message=f"Failed to connect to AI server: {str(e)}",
                code=HttpCode.server_error
            )
