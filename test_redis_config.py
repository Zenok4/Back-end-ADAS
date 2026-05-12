"""
Test Redis Configuration
Script để kiểm tra toàn bộ cấu hình Redis
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all Redis-related imports"""
    print("=== Testing Redis Imports ===")
    
    imports_to_test = [
        ("config", "is_redis_connected"),
        ("config", "redis_client"),
        ("helper.redis_helper", "redis_helper"),
        ("middlewares.redis_cache_middleware", "redis_cache"),
        ("services.redis_service", "redis_service"),
        ("endpoints.redis_endpoints", "redis_bp"),
    ]
    
    for module_name, import_name in imports_to_test:
        try:
            if module_name == "config":
                from config import is_redis_connected, redis_client
                print(f"✅ {module_name}.{import_name} - OK")
            elif module_name == "helper.redis_helper":
                from helper.redis_helper import redis_helper
                print(f"✅ {module_name}.{import_name} - OK")
            elif module_name == "middlewares.redis_cache_middleware":
                from middlewares.redis_cache_middleware import redis_cache
                print(f"✅ {module_name}.{import_name} - OK")
            elif module_name == "services.redis_service":
                from services.redis_service import redis_service
                print(f"✅ {module_name}.{import_name} - OK")
            elif module_name == "endpoints.redis_endpoints":
                from endpoints.redis_endpoints import redis_bp
                print(f"✅ {module_name}.{import_name} - OK")
        except ImportError as e:
            print(f"❌ {module_name}.{import_name} - FAILED: {e}")
        except Exception as e:
            print(f"⚠️  {module_name}.{import_name} - WARNING: {e}")


def test_redis_connection():
    """Test Redis connection"""
    print("\n=== Testing Redis Connection ===")
    
    try:
        from config import is_redis_connected, redis_client
        
        if is_redis_connected():
            print("✅ Redis is connected")
            
            # Test ping
            try:
                redis_client.ping()
                print("✅ Redis ping successful")
            except Exception as e:
                print(f"❌ Redis ping failed: {e}")
        else:
            print("❌ Redis is not connected")
            
    except Exception as e:
        print(f"❌ Failed to test Redis connection: {e}")


def test_redis_operations():
    """Test basic Redis operations"""
    print("\n=== Testing Redis Operations ===")
    
    try:
        from helper.redis_helper import redis_helper
        from config import is_redis_connected
        
        if not is_redis_connected():
            print("⚠️  Skipping operations test - Redis not connected")
            return
        
        # Test set and get
        test_key = "test:config:check"
        test_value = {"test": "data", "timestamp": "2024-01-01"}
        
        # Set
        set_result = redis_helper.set(test_key, test_value, expire=10)
        print(f"✅ Set operation: {'Success' if set_result else 'Failed'}")
        
        # Get
        get_result = redis_helper.get(test_key)
        if get_result and get_result.get("test") == "data":
            print("✅ Get operation: Success")
        else:
            print("❌ Get operation: Failed")
        
        # Exists
        exists_result = redis_helper.exists(test_key)
        print(f"✅ Exists operation: {'Key exists' if exists_result else 'Key not found'}")
        
        # TTL
        ttl_result = redis_helper.ttl(test_key)
        print(f"✅ TTL operation: {ttl_result} seconds")
        
        # Delete
        delete_result = redis_helper.delete(test_key)
        print(f"✅ Delete operation: {'Success' if delete_result else 'Failed'}")
        
        # Clean up
        redis_helper.delete(test_key)
        
    except Exception as e:
        print(f"❌ Failed to test Redis operations: {e}")


def test_redis_cache_middleware():
    """Test Redis cache middleware"""
    print("\n=== Testing Redis Cache Middleware ===")
    
    try:
        from middlewares.redis_cache_middleware import redis_cache
        from config import is_redis_connected
        
        if not is_redis_connected():
            print("⚠️  Skipping cache middleware test - Redis not connected")
            return
        
        # Test user cache
        user_id = 999
        user_data = {"id": user_id, "name": "Test User", "email": "test@example.com"}
        
        # Cache user data
        cache_result = redis_cache.cache_user_data(user_id, user_data, ttl=10)
        print(f"✅ Cache user data: {'Success' if cache_result else 'Failed'}")
        
        # Get cached user
        cached_user = redis_cache.get_cached_user(user_id)
        if cached_user and cached_user.get("id") == user_id:
            print("✅ Get cached user: Success")
        else:
            print("❌ Get cached user: Failed")
        
        # Invalidate cache
        invalidate_result = redis_cache.invalidate_user_cache(user_id)
        print(f"✅ Invalidate user cache: {'Success' if invalidate_result else 'Failed'}")
        
        # Clean up
        redis_cache.invalidate_user_cache(user_id)
        
    except Exception as e:
        print(f"❌ Failed to test Redis cache middleware: {e}")


def test_redis_service():
    """Test Redis service"""
    print("\n=== Testing Redis Service ===")
    
    try:
        from services.redis_service import redis_service
        from config import is_redis_connected
        
        if not is_redis_connected():
            print("⚠️  Skipping service test - Redis not connected")
            return
        
        # Test health check
        health_info = redis_service.health_check()
        print(f"✅ Health check: {health_info.get('status', 'unknown')}")
        
        # Test rate limiting
        test_key = "test:ratelimit:check"
        is_over_limit = redis_service.rate_limit(test_key, limit=5, window=10)
        print(f"✅ Rate limiting: {'Over limit' if is_over_limit else 'Within limit'}")
        
        # Test get rate limit info
        rate_info = redis_service.get_rate_limit_info(test_key)
        print(f"✅ Rate limit info: Current count = {rate_info.get('current_count', 0)}")
        
        # Clean up
        from helper.redis_helper import redis_helper
        redis_helper.delete(test_key)
        
    except Exception as e:
        print(f"❌ Failed to test Redis service: {e}")


def test_file_structure():
    """Test file structure"""
    print("\n=== Testing File Structure ===")
    
    files_to_check = [
        "config.py",
        "helper/redis_helper.py",
        "middlewares/redis_cache_middleware.py",
        "services/redis_service.py",
        "endpoints/redis_endpoints.py",
        "example_redis_usage.py",
        "REDIS_SETUP.md",
        "redis_production_config.py",
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - Exists")
        else:
            print(f"❌ {file_path} - Missing")


def test_requirements():
    """Test Redis requirements"""
    print("\n=== Testing Requirements ===")
    
    try:
        import redis
        print(f"✅ redis package: Version {redis.__version__}")
    except ImportError:
        print("❌ redis package: Not installed")
    
    try:
        import redis as r
        # Check if it's version 5.x
        version = r.__version__
        if version.startswith("5."):
            print(f"✅ redis package version: {version} (OK)")
        else:
            print(f"⚠️  redis package version: {version} (Expected 5.x)")
    except:
        print("❌ Failed to check redis version")


def main():
    """Main test function"""
    print("Redis Configuration Test Suite")
    print("=" * 50)
    
    test_imports()
    test_redis_connection()
    test_redis_operations()
    test_redis_cache_middleware()
    test_redis_service()
    test_file_structure()
    test_requirements()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("-" * 50)
    
    # Provide next steps
    print("\nNext Steps:")
    print("1. Install Redis server if not already installed")
    print("2. Update .env file with Redis configuration")
    print("3. Run: python example_redis_usage.py")
    print("4. Test API endpoints: GET /redis/health")
    print("5. Review REDIS_SETUP.md for detailed instructions")
    
    print("\nTo run the Flask app with Redis:")
    print("1. Start Redis server")
    print("2. Run: python app.py")
    print("3. Test: curl http://localhost:5000/test-connection")
    print("4. Test Redis: curl http://localhost:5000/redis/health")


if __name__ == "__main__":
    main()