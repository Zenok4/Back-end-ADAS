import os
from dotenv import load_dotenv
import httpx

# load file .env từ thư mục root
load_dotenv()


#############################
# Cấu hình cơ sở dữ liệu (user, password, database ghi trong file .env)
DB_CONFIG = {
    "MYSQL": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", ""),
    }
}

# Cấu hình Redis
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "password": os.getenv("REDIS_PASSWORD", None),
    "db": int(os.getenv("REDIS_DB", 0)),
    "decode_responses": True,
}

# TTL (giây)
REDIS_OTP_TTL = int(os.getenv("REDIS_OTP_TTL", 300))          # OTP: 5 phút
REDIS_SESSION_TTL = int(os.getenv("REDIS_SESSION_TTL", 604800))  # Session: 7 ngày
REDIS_PERMISSION_TTL = int(os.getenv("REDIS_PERMISSION_TTL", 300))  # Permission cache: 5 phút

# Cấu hình JWT cho xác thực người dùng
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # mặc định HS256 nếu không có
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8500").rstrip("/")
GRPC_SERVER_URL = os.getenv("GRPC_SERVER_URL", "localhost:8500").rstrip("/")

# Cấu hình Secret Key
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

# Cấu hình URL của AI Server
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "")


async_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=30.0),
    http2=True,
)
