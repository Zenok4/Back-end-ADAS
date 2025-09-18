import logging
import os

# Thư mục lưu log
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Tạo loggers
logger = logging.getLogger("backend")
logger.setLevel(logging.DEBUG)

# Formatter chung
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Handler ghi log INFO (thành công, trạng thái) → info.log
info_handler = logging.FileHandler(os.path.join(LOG_DIR, "info.log"))
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# Handler ghi log ERROR (lỗi) → error.log
error_handler = logging.FileHandler(os.path.join(LOG_DIR, "error.log"))
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Handler ghi log DEBUG (chi tiết) → debug.log
debug_handler = logging.FileHandler(os.path.join(LOG_DIR, "debug.log"))
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

# Handler in ra console (tiện debug)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Gắn handlers vào logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(debug_handler)
logger.addHandler(console_handler)
