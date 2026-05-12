"""
Ví dụ sử dụng Redis trong Back-end ADAS
"""

from config import redis_client, is_redis_connected, reconnect_redis
from helper.redis_helper import redis_helper


def example_basic_operations():
    """Ví dụ các thao tác cơ bản với Redis"""
    
    # Kiểm tra kết nối Redis
    if not is_redis_connected():
        print("Redis không kết nối. Thử kết nối lại...")
        if not reconnect_redis():
            print("Không thể kết nối Redis")
            return
    
    print("=== Ví dụ Redis Operations ===")
    
    # 1. Set và Get cơ bản
    print("\n1. Set và Get cơ bản:")
    redis_helper.set("test_key", "Hello Redis!")
    value = redis_helper.get("test_key")
    print(f"   test_key: {value}")
    
    # 2. Set với expiration
    print("\n2. Set với expiration (10 giây):")
    redis_helper.set("temp_key", "This will expire", expire=10)
    ttl = redis_helper.ttl("temp_key")
    print(f"   temp_key TTL: {ttl} giây")
    
    # 3. Kiểm tra key tồn tại
    print("\n3. Kiểm tra key tồn tại:")
    exists = redis_helper.exists("test_key")
    print(f"   test_key exists: {exists}")
    
    # 4. Xóa key
    print("\n4. Xóa key:")
    redis_helper.delete("test_key")
    exists_after = redis_helper.exists("test_key")
    print(f"   test_key exists after delete: {exists_after}")
    
    # 5. Lưu dictionary
    print("\n5. Lưu dictionary:")
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin"
    }
    redis_helper.set("user:1", user_data)
    retrieved_user = redis_helper.get("user:1")
    print(f"   User data: {retrieved_user}")
    
    # 6. Increment counter
    print("\n6. Increment counter:")
    redis_helper.set("page_views", 0)
    for i in range(3):
        new_value = redis_helper.increment("page_views")
        print(f"   Page views after increment {i+1}: {new_value}")
    
    # 7. Hash operations
    print("\n7. Hash operations:")
    redis_helper.hash_set("session:abc123", "user_id", 1)
    redis_helper.hash_set("session:abc123", "username", "johndoe")
    redis_helper.hash_set("session:abc123", "permissions", ["read", "write"])
    
    session_data = redis_helper.hash_get_all("session:abc123")
    print(f"   Session data: {session_data}")
    
    # 8. List all keys
    print("\n8. List all keys:")
    all_keys = redis_helper.keys()
    print(f"   All keys: {all_keys}")
    
    # 9. Flush all (chỉ dùng cho testing)
    print("\n9. Flush all data (testing only):")
    # redis_helper.flush_all()  # Uncomment để xóa tất cả dữ liệu
    # print("   All data flushed")


def example_cache_authentication():
    """Ví dụ cache cho authentication"""
    
    if not is_redis_connected():
        return
    
    print("\n=== Ví dụ Cache Authentication ===")
    
    # Cache JWT token blacklist
    def add_to_blacklist(token: str, expire_seconds: int = 3600):
        """Thêm token vào blacklist"""
        key = f"blacklist:{token}"
        redis_helper.set(key, "blacklisted", expire=expire_seconds)
        print(f"   Token added to blacklist: {token[:20]}...")
    
    def is_token_blacklisted(token: str) -> bool:
        """Kiểm tra token có trong blacklist không"""
        key = f"blacklist:{token}"
        return redis_helper.exists(key)
    
    # Test
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    add_to_blacklist(test_token, 60)
    
    is_blacklisted = is_token_blacklisted(test_token)
    print(f"   Token is blacklisted: {is_blacklisted}")


def example_cache_api_response():
    """Ví dụ cache cho API response"""
    
    if not is_redis_connected():
        return
    
    print("\n=== Ví dụ Cache API Response ===")
    
    def get_cached_data(key: str, ttl: int = 300):
        """Lấy dữ liệu từ cache hoặc tạo mới"""
        cached = redis_helper.get(key)
        if cached is not None:
            print(f"   Cache HIT for {key}")
            return cached
        
        print(f"   Cache MISS for {key}, generating data...")
        # Giả lập tạo dữ liệu tốn thời gian
        data = {
            "timestamp": "2024-01-01T00:00:00",
            "data": f"Generated data for {key}"
        }
        
        # Lưu vào cache
        redis_helper.set(key, data, expire=ttl)
        return data
    
    # Test
    data1 = get_cached_data("api:users:stats")
    print(f"   Data 1: {data1}")
    
    data2 = get_cached_data("api:users:stats")  # Lần thứ 2 sẽ lấy từ cache
    print(f"   Data 2: {data2}")


def example_rate_limiting():
    """Ví dụ rate limiting với Redis"""
    
    if not is_redis_connected():
        return
    
    print("\n=== Ví dụ Rate Limiting ===")
    
    def check_rate_limit(user_id: str, limit: int = 10, window: int = 60) -> bool:
        """
        Kiểm tra rate limit cho user
        
        Args:
            user_id: ID của user
            limit: Số request tối đa trong window
            window: Thời gian window (giây)
            
        Returns:
            bool: True nếu vượt quá limit, False nếu OK
        """
        key = f"ratelimit:{user_id}"
        current = redis_helper.get(key)
        
        if current is None:
            # Chưa có request trong window
            redis_helper.set(key, 1, expire=window)
            return False
        
        current_count = int(current)
        if current_count >= limit:
            return True  # Vượt quá limit
        
        # Tăng counter
        redis_helper.increment(key)
        return False
    
    # Test
    user_id = "user123"
    for i in range(12):  # Thử 12 request với limit 10
        is_over_limit = check_rate_limit(user_id, limit=10, window=60)
        if is_over_limit:
            print(f"   Request {i+1}: RATE LIMITED")
        else:
            print(f"   Request {i+1}: OK")


if __name__ == "__main__":
    print("Running Redis examples...")
    
    example_basic_operations()
    example_cache_authentication()
    example_cache_api_response()
    example_rate_limiting()
    
    print("\n✅ All examples completed!")