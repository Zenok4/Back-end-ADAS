from functools import wraps
from flask import request, jsonify
from services.authen.otp_service import OTPService

def require_phone_otp(purpose="login"):
    """
    Middleware kiểm tra OTP trước khi vào endpoint
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json() or {}
            phone = data.get("phone")
            otp_code = data.get("otp_code")
            if not phone or not otp_code:
                return jsonify({"error": "Phone and OTP required"}), 400

            user_or_error = OTPService.verify_otp(phone, otp_code, purpose)
            if isinstance(user_or_error, dict) and "error" in user_or_error:
                return jsonify(user_or_error), 401

            kwargs["current_user"] = user_or_error
            return func(*args, **kwargs)
        return wrapper
    return decorator
