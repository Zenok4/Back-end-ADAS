from flask import Blueprint, request, jsonify
from services.authen.login import LoginService
from type.http_constants import HttpCode

auth_bp = Blueprint("auth", __name__)

## Login bằng username/password
@auth_bp.route("/login/username", methods=["POST"])
def login_username():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    result = LoginService.login_with_username(username, password)
    
    if "error" in result:
        return jsonify(result), HttpCode.unauthorized
    return jsonify(result), HttpCode.success

## Login bằng email/password (có thể có verify_code)
@auth_bp.route("/login/phone/request-otp", methods=["POST"])
def request_otp():
    data = request.get_json()
    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Phone required"}), 400

    result = LoginService.request_phone_otp(phone)
    status = 200 if "message" in result else 400
    return jsonify(result), status

## Xác thực OTP và trả token
@auth_bp.route("/login/phone/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    phone = data.get("phone")
    otp_code = data.get("otp_code")
    if not phone or not otp_code:
        return jsonify({"error": "Phone and OTP required"}), 400

    result = LoginService.login_with_phone_otp(phone, otp_code)
    status = 200 if "access_token" in result else 401
    return jsonify(result), status

## Login bằng email/password + OTP (nếu có)
@auth_bp.route("/login/email/request-email-otp", methods=["POST"])
def request_email_otp():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400

    result = LoginService.request_email_otp(email)
    status = 200 if "message" in result else 400
    return jsonify(result), status

## Xác thực email/password (+ OTP) và trả token
@auth_bp.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")  # có thể None

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    result = LoginService.login_with_email(email, password, otp_code)
    status = 200 if "access_token" in result else 401
    return jsonify(result), status