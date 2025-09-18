import os
from dotenv import load_dotenv

# load file .env từ thư mục root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)


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

# Cấu hình Secret Key cho Flask Session
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "default_secret_key")