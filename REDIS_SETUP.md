# Redis Configuration for Back-end ADAS

## Overview
Redis đã được tích hợp vào back-end ADAS để cung cấp caching, session management, rate limiting và các tính năng khác.

## Cài đặt Redis

### 1. Cài đặt Redis Server
#### Trên Windows:
1. Tải Redis for Windows từ: https://github.com/microsoftarchive/redis/releases
2. Tải file `Redis-x64-3.0.504.msi` và cài đặt
3. Redis sẽ chạy như một service trên port 6379

#### Trên Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Mac
brew install redis
brew services start redis
```

### 2. Cài đặt Redis Python Client
Redis client đã được thêm vào `requirements.txt`:
```bash
pip install redis==5.2.0
```

## Cấu hình

### 1. Cấu hình môi trường
Các biến môi trường Redis trong file `.env`:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Để trống nếu không có password
REDIS_DB=0
```

### 2. Cấu hình kết nối
File `config.py` đã được cập nhật với cấu hình Redis:
```python
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "password": os.getenv("REDIS_PASSWORD", None),
    "db": int(os.getenv("REDIS_DB", 0)),
    "decode_responses": True,
    "socket_timeout": 5,
    "socket_connect_timeout": 5,
    "retry_on_timeout": True,
    "max_connections": 10,
}
```

## Các tính năng đã được tích hợp

### 1. Redis Helper (`helper/redis_helper.py`)
Cung cấp các hàm tiện ích cơ bản:
```python
from helper.redis_helper import redis_helper

# Set và Get
redis_helper.set("key", "value", expire=60)
value = redis_helper.get("key")

# Hash operations
redis_helper.hash_set("hash_name", "field", "value")
redis_helper.hash_get("hash_name", "field")

# Kiểm tra key
exists = redis_helper.exists("key")
ttl = redis_helper.ttl("key")
```

### 2. Redis Cache Middleware (`middlewares/redis_cache_middleware.py`)
Cung cấp decorators cho caching:
```python
from middlewares.redis_cache_middleware import cache_response, invalidate_cache

@cache_response(ttl=300)  # Cache 5 phút
def get_users():
    return jsonify(users)

@invalidate_cache("users:*")  # Xóa cache khi có thay đổi
def update_user():
    # Update logic
    return jsonify(result)
```

### 3. Redis Service (`services/redis_service.py`)
Service layer cho các operations phức tạp:
```python
from services.redis_service import redis_service

# Cache user session
redis_service.cache_user_session(user_id, session_data)

# Rate limiting
is_over_limit = redis_service.rate_limit("user:123", limit=10, window=60)

# Cache AI model results
redis_service.cache_ai_model_result("sign_detection", input_hash, result)
```

### 4. Redis Management API
Các endpoints để quản lý Redis:
- `GET /redis/health` - Kiểm tra sức khỏe Redis
- `GET /redis/stats` - Lấy thống kê Redis
- `POST /redis/cache/clear` - Xóa cache theo pattern
- `GET /redis/patterns` - Lấy danh sách cache patterns

## Sử dụng trong ứng dụng

### 1. Cache Authentication
```python
from middlewares.redis_cache_middleware import redis_cache

# Thêm token vào blacklist
redis_cache.add_to_blacklist(token, ttl=3600)

# Kiểm tra token blacklisted
is_blacklisted = redis_cache.is_token_blacklisted(token)
```

### 2. Cache User Data
```python
# Cache user data
redis_cache.cache_user_data(user_id, user_data, ttl=3600)

# Get cached user
cached_user = redis_cache.get_cached_user(user_id)

# Invalidate cache
redis_cache.invalidate_user_cache(user_id)
```

### 3. Rate Limiting
```python
from services.redis_service import redis_service

def check_rate_limit(user_id, limit=10, window=60):
    key = f"ratelimit:{user_id}"
    return redis_service.rate_limit(key, limit, window)
```

### 4. Cache API Responses
```python
from middlewares.redis_cache_middleware import cache_response

@cache_response(ttl=300)  # Cache 5 phút
@app.route("/api/users")
def get_users():
    # Logic lấy users
    return jsonify(users)
```

## Testing Redis

### 1. Test Connection
```bash
# Kiểm tra kết nối
curl http://localhost:5000/test-connection

# Kiểm tra Redis health
curl http://localhost:5000/redis/health
```

### 2. Run Example
```bash
python example_redis_usage.py
```

### 3. Test Cache Operations
```bash
# Test cache
curl -X POST http://localhost:5000/redis/test/cache \
  -H "Content-Type: application/json" \
  -d '{"key": "test", "value": "test_value", "ttl": 60}'
```

## Monitoring và Maintenance

### 1. Xem Redis Statistics
```bash
curl http://localhost:5000/redis/stats
```

### 2. Xóa Cache
```bash
# Xóa tất cả cache
curl -X POST http://localhost:5000/redis/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"pattern": "*"}'

# Xóa cache user
curl -X DELETE http://localhost:5000/redis/cache/user/123
```

### 3. Xem Memory Usage
```bash
curl http://localhost:5000/redis/memory
```

## Troubleshooting

### 1. Redis không kết nối
1. Kiểm tra Redis service đang chạy:
   ```bash
   # Windows
   services.msc  # Tìm Redis service
   
   # Linux
   sudo systemctl status redis
   ```

2. Kiểm tra port 6379:
   ```bash
   netstat -an | findstr 6379  # Windows
   sudo netstat -tlnp | grep 6379  # Linux
   ```

3. Kiểm tra firewall:
   ```bash
   # Mở port 6379 nếu cần
   ```

### 2. Lỗi Connection Refused
1. Kiểm tra Redis host và port trong `.env`
2. Kiểm tra Redis password nếu có
3. Kiểm tra Redis đang lắng nghe trên đúng interface

### 3. Performance Issues
1. Giảm TTL cho cache không quan trọng
2. Sử dụng connection pooling
3. Monitor memory usage

## Best Practices

### 1. Cache Strategy
- **User data**: TTL 1 giờ
- **Session data**: TTL 24 giờ
- **API responses**: TTL 5 phút
- **AI model results**: TTL 30 phút
- **Statistics**: TTL 5 phút

### 2. Key Naming Convention
- `user:{user_id}` - User data
- `session:{session_id}` - Session data
- `detection:{type}:{id}` - Detection results
- `trip:{trip_id}` - Trip data
- `stats:{type}` - Statistics
- `ai:{model}:{hash}` - AI model results
- `config:{key}` - Configuration
- `blacklist:{token}` - Blacklisted tokens
- `api:{endpoint}:{hash}` - API cache

### 3. Memory Management
- Đặt TTL cho tất cả cache keys
- Sử dụng `maxmemory` policy trong Redis config
- Monitor memory usage thường xuyên
- Xóa cache cũ định kỳ

## Security Considerations

### 1. Authentication
- Sử dụng Redis password nếu chạy trên production
- Giới hạn access với firewall rules
- Sử dụng SSL/TLS cho remote connections

### 2. Data Protection
- Không lưu sensitive data trong Redis
- Mã hóa sensitive data trước khi cache
- Sử dụng TTL ngắn cho sensitive data

### 3. Access Control
- Giới hạn IP addresses có thể kết nối
- Sử dụng Redis ACL nếu có
- Monitor access logs

## Production Deployment

### 1. Redis Configuration
```conf
# redis.conf
bind 127.0.0.1
port 6379
requirepass your_strong_password
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 2. High Availability
- Sử dụng Redis Sentinel cho failover
- Hoặc Redis Cluster cho sharding
- Backup định kỳ RDB files

### 3. Monitoring
- Sử dụng Redis INFO command
- Monitor memory usage
- Monitor hit/miss ratio
- Alert trên critical errors

## References
- [Redis Documentation](https://redis.io/documentation)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [Redis Security](https://redis.io/docs/management/security/)