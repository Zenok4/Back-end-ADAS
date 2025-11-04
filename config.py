import os
from dotenv import load_dotenv

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

# Cấu hình JWT cho xác thực người dùng
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # mặc định HS256 nếu không có
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8500").rstrip("/")

# Cấu hình Secret Key
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

# Cấu hình URL của AI Server
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "")
