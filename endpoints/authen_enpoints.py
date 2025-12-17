from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.authen.login import LoginService
from services.authen.register import RegisterService
from services.authen.session_service import SessionService
from services.authen.user_service import UserService
from type.http_constants import HttpCode
from helper.normalization_response import response_error, response_success

authen_bp = Blueprint("authen_bp", __name__, url_prefix="/authen")

## ================== Login Username ==================
@authen_bp.route("/login/username", methods=["POST"])
def login_username():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(response_error("Vui lòng nhập tên đăng nhập và mật khẩu", code=HttpCode.bad_request)), HttpCode.bad_request

    # [FIX] Truyền request
    result = LoginService.login_with_username(username, password, request)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.unauthorized)), HttpCode.unauthorized

    return jsonify(response_success(data=result, message="Đăng nhập thành công", code=HttpCode.success)), HttpCode.success


# ================== Login Phone OTP ==================
@authen_bp.route("/login/phone/otp", methods=["POST"])
def request_phone_otp():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")

    if not phone:
        return jsonify(response_error("Vui lòng nhập số điện thoại", code=HttpCode.bad_request)), HttpCode.bad_request

    result = LoginService.request_phone_otp(phone)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.bad_request)), HttpCode.bad_request

    return jsonify(response_success(message=result.get("message", "OTP sent"), code=HttpCode.success)), HttpCode.success

@authen_bp.route("/login/phone/verify", methods=["POST"])
def verify_phone_otp():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    otp_code = data.get("otp_code")

    if not phone or not otp_code:
        return jsonify(response_error("Thiếu số điện thoại hoặc OTP", code=HttpCode.bad_request)), HttpCode.bad_request

    # [FIX] Truyền request
    result = LoginService.login_with_phone_otp(phone, otp_code, request)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.unauthorized)), HttpCode.unauthorized

    return jsonify(response_success(data=result, message="Đăng nhập thành công", code=HttpCode.success)), HttpCode.success


# ================== Login Email ==================
@authen_bp.route("/login/email/otp", methods=["POST"])
def request_email_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email")

    if not email:
        return jsonify(response_error("Vui lòng nhập email", code=HttpCode.bad_request)), HttpCode.bad_request

    result = LoginService.request_email_otp(email)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.bad_request)), HttpCode.bad_request

    return jsonify(response_success(message=result.get("message", "OTP sent"), code=HttpCode.success)), HttpCode.success

@authen_bp.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")

    if not email or not password:
        return jsonify(response_error("Vui lòng nhập email và mật khẩu", code=HttpCode.bad_request)), HttpCode.bad_request

    # [FIX] Truyền request
    result = LoginService.login_with_email(email, password, request, otp_code)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.unauthorized)), HttpCode.unauthorized

    return jsonify(response_success(data=result, message="Đăng nhập thành công", code=HttpCode.success)), HttpCode.success


# ================== Refresh & Logout ==================
@authen_bp.route("/refresh", methods=["POST"])
def refresh_token():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify(response_error("Thiếu Session ID", code=HttpCode.bad_request)), HttpCode.bad_request

    session = SessionService.validate_session(session_id)
    if not session:
        return jsonify(response_error("Phiên đăng nhập không hợp lệ hoặc đã hết hạn", code=HttpCode.unauthorized)), HttpCode.unauthorized
    
    if SessionService.check_rate_limit(session):
        return jsonify(response_error("Gửi quá nhiều yêu cầu, vui lòng đợi", code=HttpCode.too_many_requests)), HttpCode.too_many_requests
    
    if SessionService.validate_session_context(session, request) is False:
        return jsonify(response_error("Phát hiện truy cập bất thường (User-Agent thay đổi)", code=HttpCode.unauthorized)), HttpCode.unauthorized

    result = LoginService.refresh_access_token(session)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.internal_server_error)), HttpCode.internal_server_error

    return jsonify(response_success(data=result, message="Làm mới token thành công", code=HttpCode.success)), HttpCode.success

@authen_bp.route("/logout", methods=["POST"])
def logout():
    data = request.get_json() or {}
    session_id = data.get("session_id")
    if not session_id:
        return jsonify(response_error("Thiếu Session ID", code=HttpCode.bad_request)), HttpCode.bad_request

    result = LoginService.logout(session_id)
    if "error" in result:
        return jsonify(response_error(result["error"], code=HttpCode.unauthorized)), HttpCode.unauthorized

    return jsonify(response_success(message="Đăng xuất thành công", code=HttpCode.success)), HttpCode.success


# ================== Me & Register & Forgot Pass (Giữ nguyên) ==================
# (Phần này bạn có thể giữ nguyên như code cũ, hoặc copy từ User Service)
# Nhớ import và sử dụng đúng tên hàm nếu có thay đổi.

## ================== Me (Current User) ==================
@authen_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Lấy thông tin người dùng hiện tại dựa trên access token (JWT).
    - Header: Authorization: Bearer <access_token>
    - Output:
        {
            "success": true,
            "message": "Fetched user successfully",
            "code": 200,
            "user": { ... }
        }
    """
    try:
        user_id = get_jwt_identity()  # Lấy user_id từ token
        if not user_id:
            result = response_error("Missing or invalid token", code=HttpCode.unauthorized)
            return jsonify(result), result["error"]["code"]

        # Gọi service để lấy thông tin chi tiết user
        result = UserService.get_user_by_id(int(user_id), include_roles=True)
        status = result.get("code", HttpCode.success)

        return jsonify(result), status

    except Exception as e:
        result = response_error(f"Failed to fetch current user: {str(e)}", code=HttpCode.internal_server_error)
        return jsonify(result), result["error"]["code"]



# ================== REGISTER ==================
@authen_bp.route("/register/username", methods=["POST"])
def register_username():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify(response_error("Username and password required", code=400)), 400
    result = RegisterService.register_with_username(username, password)
    return jsonify(result), result.get("code", 400)

@authen_bp.route("/register/email", methods=["POST"])
def register_email():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    otp_code = data.get("otp_code")
    if not email or not password or not otp_code:
        return jsonify(response_error("Email, password and OTP required", code=400)), 400
    result = RegisterService.register_with_email(email, password, otp_code)
    return jsonify(result), result.get("code", 400)

@authen_bp.route("/register/phone", methods=["POST"])
def register_phone():
    data = request.get_json() or {}
    phone = data.get("phone")
    otp_code = data.get("otp_code")
    password = data.get("password")  # Lấy thêm password từ frontend
    
    if not phone or not otp_code or not password:
        return jsonify(response_error("Phone, password and OTP required", code=400)), 400
    
    # Gọi hàm register_with_phone (đã sửa ở bước 1)
    result = RegisterService.register_with_phone(phone, password, otp_code)
    return jsonify(result), result.get("code", 400)

# ================== FORGOT PASSWORD ==================
@authen_bp.route("/forgot-password/email/send-otp", methods=["POST"])
def forgot_password_email_send_otp():
    data = request.get_json() or {}
    # SỬA: Thêm .strip() và .lower() để xóa khoảng trắng và chuyển thường
    email = data.get("email", "").strip().lower()
    
    if not email: 
        return jsonify(response_error("Email required", code=400)), 400
        
    result = LoginService.request_forgot_password_email(email)
    
    # Kiểm tra result trả về để response đúng HTTP code
    status_code = 400 if "error" in result else 200
    return jsonify(result), status_code

@authen_bp.route("/forgot-password/email/reset", methods=["POST"])
def forgot_password_email_reset():
    data = request.get_json() or {}
    email = data.get("email")
    otp = data.get("otp_code")
    pwd = data.get("new_password")
    if not email or not otp or not pwd: return jsonify(response_error("Missing data", code=400)), 400
    result = LoginService.reset_password_email(email, otp, pwd)
    return jsonify(result), result.get("code", 400) if "error" in result else 200

@authen_bp.route("/forgot-password/phone/reset", methods=["POST"])
def forgot_password_phone_reset():
    data = request.get_json() or {}
    phone = data.get("phone")
    otp = data.get("otp_code")
    pwd = data.get("new_password")
    if not phone or not otp or not pwd: return jsonify(response_error("Missing data", code=400)), 400
    result = LoginService.reset_password_phone(phone, otp, pwd)
    return jsonify(result), result.get("code", 400) if "error" in result else 200
@authen_bp.route("/register/email/otp", methods=["POST"])
def send_otp_register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    
    if not email:
        return jsonify(response_error("Vui lòng nhập email", HttpCode.bad_request)), HttpCode.bad_request

    # Gọi hàm mới trong RegisterService
    result = RegisterService.send_otp_for_register(email)
    
    if not result.get("success"):
        return jsonify(result), result.get("code", HttpCode.bad_request)
    
    return jsonify(result), result.get("code", HttpCode.success)