from flask import Blueprint, request, jsonify
from services.ai.sign_service import SignService
from helper.normalization_response import response_error
from type.http_constants import HttpCode
import imghdr

sign_bp = Blueprint("sign", __name__)
sign_service = SignService()

@sign_bp.route("/predict", methods=["POST"])
def sign_predict():
    """
    Endpoint nhận diện biển báo giao thông.
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Field: 'image' - File ảnh cần nhận diện
        
    Response:
        - 200: Kết quả nhận diện thành công
        - 400: Thiếu file ảnh hoặc không phải ảnh hợp lệ
        - 502: Lỗi khi gọi AI server
    """
    try:
        image_file = request.files.get("image")
        if not image_file:
            return jsonify(response_error(
                message="No image file provided",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        # Kiểm tra loại file có phải ảnh không
        try:
            header = image_file.read(512)
            image_file.seek(0)
            file_type = imghdr.what(None, header)
            if file_type is None:
                return jsonify(response_error(
                    message="Invalid or unsupported image file",
                    code=HttpCode.bad_request
                )), HttpCode.bad_request
        except Exception:
            return jsonify(response_error(
                message="Error reading image file",
                code=HttpCode.bad_request
            )), HttpCode.bad_request

        # Gọi service để xử lý
        result = sign_service.predict_sign(image_file)

        # Nếu AI trả lỗi
        if isinstance(result, dict) and result.get("error"):
            return jsonify(response_error(
                message=result["error"],
                code=HttpCode.bad_gateway
            )), HttpCode.bad_gateway

        # Trả toàn bộ dữ liệu (có confidence, box, class_name...)
        return jsonify({
            "code": HttpCode.success,
            "data": result
        }), HttpCode.success

    except Exception as e:
        return jsonify(
            response_error(
                message=str(e),
                code=HttpCode.internal_server_error
            )
        ), HttpCode.internal_server_error
