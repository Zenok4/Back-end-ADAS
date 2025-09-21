# routes/auth.py
from flask import Blueprint, request, jsonify
from services.authen.login import LoginService
from services.authen.session_service import SessionService
from services.authen.user_service import UserService
from services.authen.register import RegisterService
from type.http_constants import HttpCode

auth_bp = Blueprint("auth", __name__)


## ================== Username/Password ==================
@auth_bp.route("/login/username", methods=["POST"])
def login_username():
    """
    Đăng nhập bằng username + password.
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), HttpCode.bad_request

    result = LoginService.login_with_username(username, password)
    status = HttpCode.success if result.get("success") else HttpCode.unauthorized
    return jsonify(result), status


## ================== Phone OTP ==================
@auth_bp.route("/login/phone/otp", methods=["POST"])
def request_phone_otp():
    """
    Gửi OTP về số điện thoại để đăng nhập.
    """
    data = request.get_json() or {}
    phone = data.get("phone")

    if not phone:
        return jsonify({"success": False, "error": "Phone required"}), HttpCode.bad_request

    result = LoginService.request_phone_otp(phone)
    status = HttpCode.success if "message" in result else HttpCode.bad_request
    return jsonify(result), status


@auth_bp.route("/login/phone/verify", methods=["POST"])
def verify_phone_otp():
    """
    Xác thực OTP để đăng nhập bằng số điện thoại.
    """
    data = request.get_json() or {}
    phone = data.get("phone")
    otp_code = data.get("otp_code")

    if not phone or not otp_code:
        return jsonify({"success": False, "error": "Phone and OTP required"}), HttpCode.bad_request

    result = LoginService.login_with_phone_otp(phone, otp_code)
    status = HttpCode.success if result.get("success") else HttpCode.unauthorized
    return jsonify(result), status


## ================== Email ==================
@auth_bp.route("/login/email/otp", methods=["POST"])
def request_email_otp():
    """
    Gửi OTP về email để xác thực.
    """
    data = request.get_json() or {}
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "error": "Email required"}), HttpCode.bad_request

    result = LoginService.request_email_otp(email)
    status = HttpCode.success if "message" in result else HttpCode.bad_request
    return jsonify(result), status


@auth_bp.route("/login/email", methods=["POST"])
def login_email():
    """
    Đăng nhập bằng email + password + (OTP nếu có).
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), HttpCode.bad_request

    result = LoginService.login_with_email(email, password, otp_code)
    status = HttpCode.success if result.get("success") else HttpCode.unauthorized
    return jsonify(result), status


## ================== Refresh Token ==================
@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Cấp lại access_token mới bằng refresh_token.
    - Input JSON: { "refresh_token": "..." }
    - Trả về: { access_token, user } nếu refresh_token hợp lệ
    - Lỗi: 400 nếu thiếu dữ liệu, 401 nếu refresh_token không hợp lệ/hết hạn
    """
    data = request.get_json() or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), HttpCode.bad_request

    result = LoginService.refresh_access_token(refresh_token)
    status = HttpCode.success if "access_token" in result else HttpCode.unauthorized
    return jsonify(result), status


## ================== Logout ==================
@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Đăng xuất người dùng: thu hồi (revoke) session trong DB.
    - Input JSON: { "session_id": "..." }
    - Trả về: { success: true } nếu logout thành công
    """
    data = request.get_json() or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"}), HttpCode.bad_request

    success = SessionService.revoke_session(session_id)
    if not success:
        return jsonify({"success": False, "error": "Invalid or expired session"}), HttpCode.unauthorized

    return jsonify({"success": True, "message": "Logged out successfully"}), HttpCode.success

## ================== Me (Current User) ==================
@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """
    Lấy thông tin user hiện tại dựa trên session_id.
    - Input: { "session_id": "..." } hoặc query param/session header
    - Output: { "user": {...} }
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or request.headers.get("X-Session-Id")

    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"}), HttpCode.bad_request

    result = UserService.get_user_by_session(session_id)
    status = HttpCode.success if result.get("success") else HttpCode.unauthorized
    return jsonify(result), status


## ================== Register ==================
@auth_bp.route("/register/username", methods=["POST"])
def register_username():
    """
    Đăng ký bằng username + password.
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), HttpCode.bad_request

    result = RegisterService.register_with_username(username, password)
    status = HttpCode.success if "user" in result else HttpCode.bad_request
    return jsonify(result), status


@auth_bp.route("/register/email", methods=["POST"])
def register_email():
    """
    Đăng ký bằng email + password + OTP.
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")

    if not email or not password or not otp_code:
        return jsonify({"success": False, "error": "Email, password and OTP required"}), HttpCode.bad_request

    result = RegisterService.register_with_email(email, password, otp_code)
    status = HttpCode.success if "user" in result else HttpCode.bad_request
    return jsonify(result), status


@auth_bp.route("/register/phone", methods=["POST"])
def register_phone():
    """
    Đăng ký bằng số điện thoại + OTP.
    """
    data = request.get_json() or {}
    phone = data.get("phone")
    otp_code = data.get("otp_code")

    if not phone or not otp_code:
        return jsonify({"success": False, "error": "Phone and OTP required"}), HttpCode.bad_request

    result = RegisterService.register_with_phone(phone, otp_code)
    status = HttpCode.success if "user" in result else HttpCode.bad_request
    return jsonify(result), status
