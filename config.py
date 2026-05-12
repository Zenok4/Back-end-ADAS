import os
from dotenv import load_dotenv
import httpx
import redis
from typing import Optional

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
    "decode_responses": True,  # Decode responses to strings
    "socket_timeout": 5,  # Timeout for socket operations
    "socket_connect_timeout": 5,  # Timeout for connection
    "retry_on_timeout": True,  # Retry on timeout
    "max_connections": 10,  # Maximum number of connections in pool
}

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

# Redis client
redis_client: Optional[redis.Redis] = None

def init_redis() -> bool:
    """
    Initialize Redis connection
    
    Returns:
        bool: True if connection successful
    """
    global redis_client
    try:
        redis_client = redis.Redis(**REDIS_CONFIG)
        # Test connection
        redis_client.ping()
        print("✅ Redis connected successfully")
        return True
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        redis_client = None
        return False
    except Exception as e:
        print(f"❌ Redis error: {e}")
        redis_client = None
        return False

# Initialize Redis on import
init_redis()

# Redis helper functions
def get_redis() -> Optional[redis.Redis]:
    """
    Get Redis client instance
    
    Returns:
        Optional[redis.Redis]: Redis client or None if not connected
    """
    return redis_client

def is_redis_connected() -> bool:
    """
    Check if Redis is connected
    
    Returns:
        bool: True if connected
    """
    if not redis_client:
        return False
    try:
        redis_client.ping()
        return True
    except:
        return False

def reconnect_redis() -> bool:
    """
    Reconnect to Redis
    
    Returns:
        bool: True if reconnection successful
    """
    return init_redis()

async_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=30.0),
    http2=True,
)
