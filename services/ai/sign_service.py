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
    
    def predict_sign(self, image_file):
        """
        Gửi ảnh đến AI server để nhận diện biển báo.
        
        Args:
            image_file: File ảnh từ request (FileStorage object)
            
        Returns:
            dict: Kết quả nhận diện hoặc thông tin lỗi
        """
        
        # Đọc toàn bộ ảnh để đảm bảo stream không bị rỗng
        image_bytes = image_file.read()
        image_file.seek(0)  # reset lại để backend có thể đọc tiếp nếu cần

        files = {"image": (image_file.filename, image_bytes, image_file.mimetype)}

        try:
            # Gửi request đến AI server
            response = requests.post(self.ai_server_url, files=files, timeout=30)

            # Kiểm tra response status
            if not response.ok:
                body = None
                try:
                    body = response.text
                except Exception:
                    body = "<unable to read response body>"
                return response_error(
                    code=response.status_code,
                    message="Error from AI server"
                )

            # Parse JSON response
            try:
                return response_success(
                    data=response.json(), 
                    key="data", 
                    message="Analyze sign success", 
                    code=HttpCode.success
                )
            except ValueError as e:
                return {
                    "error": "AI server returned invalid JSON",
                    "status_code": response.status_code,
                    "body": response.text,
                    "url": self.ai_server_url,
                }

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to connect to AI server: {str(e)}", 
                "url": self.ai_server_url
            }
