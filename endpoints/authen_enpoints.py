from datetime import timedelta
from flask import Blueprint, request, jsonify
from services.authen.login import LoginService
from services.authen.session_service import SessionService
from services.authen.user_service import UserService
from services.authen.register import RegisterService
from type.http_constants import HttpCode
from helper.normalization_response import response_error, response_success

authen_bp = Blueprint("authen_bp", __name__)


## ================== Username/Password ==================
@authen_bp.route("/login/username", methods=["POST"])
def login_username():
    """
    Đăng nhập bằng username + password.
    - Input JSON: { "username": "...", "password": "..." }
    - Trả về: { success: true, message: string, code: int, data: { session_id, user, access_token, refresh_token, expires_in } } nếu thành công
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(
            response_error(
                message="Username and password required",
                code=HttpCode.bad_request,
                data={}
            )
        ), HttpCode.bad_request

    result = LoginService.login_with_username(username, password)
    if "error" in result:
        return jsonify(
            response_error(
                message=result["error"],
                code=HttpCode.unauthorized,
                data={}
            )
        ), HttpCode.unauthorized

    return jsonify(
        response_success(
            data={
                "session_id": result["session_id"],
                "user": result["user"],
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "expires_in": result["expires_in"]
            },
            message="Login successful",
            code=HttpCode.success
        )
    ), HttpCode.success


# ================== Phone OTP ==================
@authen_bp.route("/login/phone/otp", methods=["POST"])
def request_phone_otp():
    """
    Gửi OTP về số điện thoại để đăng nhập.
    - Input JSON: { "phone": "..." }
    - Trả về: { success: true, message: string, code: int, data: {} } nếu gửi OTP thành công
    """
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")

    if not phone:
        return jsonify(
            response_error(
                message="Phone required",
                code=HttpCode.bad_request,
                data={}
            )
        ), HttpCode.bad_request

    result = LoginService.request_phone_otp(phone)
    if "error" in result:
        return jsonify(
            response_error(
                message=result["error"],
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    return jsonify(
        response_success(
            message=result.get("message", "OTP sent successfully"),
            code=HttpCode.success
        )
    ), HttpCode.success

@authen_bp.route("/login/phone/verify", methods=["POST"])
def verify_phone_otp():
    """
    Xác thực OTP để đăng nhập bằng số điện thoại.
    - Input JSON: { "phone": "...", "otp_code": "..." }
    - Trả về: { success: true, message: string, code: int, data: { session_id, user, access_token, refresh_token, expires_in } } nếu thành công
    """
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    otp_code = data.get("otp_code")

    if not phone or not otp_code:
        return jsonify(
            response_error(
                message="Phone and OTP required",
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    result = LoginService.login_with_phone_otp(phone, otp_code)
    if "error" in result:
        return jsonify(
            response_error(
                message=result["error"],
                code=HttpCode.unauthorized,
            )
        ), HttpCode.unauthorized

    return jsonify(
        response_success(
            data={
                "session_id": result["session_id"],
                "user": result["user"],
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "expires_in": result["expires_in"]
            },
            message="Login successful",
            code=HttpCode.success
        )
    ), HttpCode.success

# ================== Email ==================
@authen_bp.route("/login/email/otp", methods=["POST"])
def request_email_otp():
    """
    Gửi OTP về email để xác thực.
    - Input JSON: { "email": "..." }
    - Trả về: { success: true, message: string, code: int, data: {} } nếu gửi OTP thành công
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")

    if not email:
        return jsonify(
            response_error(
                message="Email required",
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    result = LoginService.request_email_otp(email)
    if "error" in result:
        return jsonify(
            response_error(
                message=result["error"],
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    return jsonify(
        response_success(
            message=result.get("message", "OTP sent successfully"),
            code=HttpCode.success
        )
    ), HttpCode.success

@authen_bp.route("/login/email", methods=["POST"])
def login_email():
    """
    Đăng nhập bằng email + password + (OTP nếu có).
    - Input JSON: { "email": "...", "password": "...", "otp_code": "..." (optional) }
    - Trả về: { success: true, message: string, code: int, data: { session_id, user, access_token, refresh_token, expires_in } } nếu thành công
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")

    if not email or not password:
        return jsonify(
            response_error(
                message="Email and password required",
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    result = LoginService.login_with_email(email, password, otp_code)
    if "error" in result:
        return jsonify(
            response_error(
                message=result["error"],
                code=HttpCode.unauthorized,
            )
        ), HttpCode.unauthorized

    return jsonify(
        response_success(
            data={
                "session_id": result["session_id"],
                "user": result["user"],
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "expires_in": result["expires_in"]
            },
            message="Login successful",
            code=HttpCode.success
        )
    ), HttpCode.success

# ================== Refresh Token ==================
@authen_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Cấp lại access_token mới bằng refresh_token.
    - Input JSON: { "refresh_token": "..." }
    - Trả về: { success: true, message: string, code: int, data: { access_token, expires_in } } nếu thành công
    """
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify(
            response_error(
                message="Refresh token required",
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    result = LoginService.refresh_access_token(refresh_token)
    if "error" in result:
        return jsonify(
            response_error(
                message=result["error"],
                code=HttpCode.unauthorized,
            )
        ), HttpCode.unauthorized

    return jsonify(
        response_success(
            data={
                "access_token": result["access_token"],
                "expires_in": timedelta(minutes=15).total_seconds()
            },
            message="Token refreshed successfully",
            code=HttpCode.success
        )
    ), HttpCode.success


## ================== Logout ==================
@authen_bp.route("/logout", methods=["POST"])
def logout():
    """
    Đăng xuất người dùng: thu hồi (revoke) session trong DB.
    - Input JSON: { "session_id": "..." }
    - Trả về: { success: true } nếu logout thành công
    """
    data = request.get_json() or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify(
            response_error(
                message="Session ID required",
                code=HttpCode.bad_request,
            )
        ), HttpCode.bad_request

    success = SessionService.revoke_session(session_id)
    if not success:
        return jsonify(
            response_error(
                message="Invalid or expired session",
                code=HttpCode.unauthorized,
            )
        ), HttpCode.unauthorized

    return jsonify(
        response_success(
            message="Logged out successfully",
            code=HttpCode.success
        )
    ), HttpCode.success

## ================== Me (Current User) ==================
@authen_bp.route("/me", methods=["GET"])
def get_current_user():
    """
    Lấy thông tin user hiện tại dựa trên session_id.
    - Input: { "session_id": "..." } hoặc query param/session header
    - Output: { "user": {...} }
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or request.headers.get("X-Session-Id")

    if not session_id:
        return jsonify(response_error(message="Session ID required", code=HttpCode.bad_request)), HttpCode.bad_request

    result = UserService.get_user_by_session(session_id)
    status = result.get("code", HttpCode.unauthorized)
    return jsonify(result), status


## ================== Register ==================
@authen_bp.route("/register/username", methods=["POST"])
def register_username():
    """
    Đăng ký bằng username + password.
    - Input JSON: { "username": "...", "password": "..." }
    - Trả về: { success: true, message: string, code: int, data: { user } } nếu thành công
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        result = response_error("Username and password required", code=HttpCode.bad_request)
        return jsonify(result), result["error"]["code"]

    result = RegisterService.register_with_username(username, password)
    status = result.get("code", HttpCode.bad_request)
    return jsonify(result), status


@authen_bp.route("/register/email", methods=["POST"])
def register_email():
    """
    Đăng ký bằng email + password + OTP.
    - Input JSON: { "email": "...", "password": "...", "otp_code": "..." }
    - Trả về: { success: true, message: string, code: int, data: { user } } nếu thành công
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")

    if not email or not password or not otp_code:
        result = response_error("Email, password and OTP required", code=HttpCode.bad_request)
        return jsonify(result), result["error"]["code"]

    result = RegisterService.register_with_email(email, password, otp_code)
    status = result.get("code", HttpCode.bad_request)
    return jsonify(result), status


@authen_bp.route("/register/phone", methods=["POST"])
def register_phone():
    """
    Đăng ký bằng số điện thoại + OTP.
    - Input JSON: { "phone": "...", "otp_code": "..." }
    - Trả về: { success: true, message: string, code: int, data: { user } } nếu thành công
    """
    data = request.get_json() or {}
    phone = data.get("phone")
    otp_code = data.get("otp_code")

    if not phone or not otp_code:
        result = response_error("Phone and OTP required", code=HttpCode.bad_request)
        return jsonify(result), result["error"]["code"]

    result = RegisterService.register_with_phone(phone, otp_code)
    status = result.get("code", HttpCode.bad_request)
    return jsonify(result), status
