from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_session import Session
from logger import logger
import time
from werkzeug.exceptions import HTTPException
from type.http_constants import HttpCode
from config import JWT_SECRET_KEY
from database import get_mysql_connection
from endpoints.authen_enpoints import authen_bp
from endpoints.author_enpoints import author_bp
from endpoints.usermanage_endpoints import user_bp
from endpoints.sign_endpoints import sign_bp
from models import init_dtb

app = Flask(__name__)

# ========== Cấu hình JWT ==========
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# ========== Đăng ký các blueprint ==========
app.register_blueprint(authen_bp, url_prefix="/authen")
app.register_blueprint(author_bp, url_prefix="/author")
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(sign_bp, url_prefix="/sign")


# ========== TEST Connection ==========
def test_connection():
    try:
        mysql_conn = get_mysql_connection()
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SELECT COUNT(*) FROM users")
        mysql_cursor.fetchone()
        mysql_conn.close()

        return {"status": "success", "message": "Database connections successful!"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


@app.route("/test-connection", methods=["GET"])
def test_connection_api():
    """
    Kiểm tra kết nối giữa server và database
    """
    return jsonify(test_connection())


############################################
# ========== Init ==========
# Init Database cho hệ thống
init_dtb(app)


############################################
# ========== Logging ==========
# Logging middleware khi request và response
@app.before_request
def log_request():
    request.start_time = time.time()
    logger.info(
        f"[REQUEST] {request.method} {request.path} - IP: {request.remote_addr}"
    )


@app.after_request
def log_response(response):
    duration = round(time.time() - request.start_time, 3)
    logger.info(
        f"[RESPONSE] {request.method} {request.path} - Status: {response.status_code} - Time: {duration}s"
    )
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        # lỗi HTTP custom, log message luôn
        logger.error(
            f"[CUSTOM ERROR] {request.method} {request.path} - {e.description}"
        )
        return {"error": e.description}, e.code
    else:
        # lỗi hệ thống
        logger.error(f"[SYSTEM ERROR] {request.method} {request.path} - {str(e)}")
        return {"error": "Internal Server Error"}, HttpCode.internal_server_error


############################################
# Chạy ứng dụng
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
