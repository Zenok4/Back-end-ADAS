"""
Redis Cache Middleware
Middleware để cache response và quản lý cache với Redis
"""

import json
import hashlib
from functools import wraps
from flask import request, current_app
from typing import Callable, Any, Optional, Dict
from config import is_redis_connected
from helper.redis_helper import redis_helper


def cache_response(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator để cache response của API
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Chỉ cache nếu Redis đã kết nối
            if not is_redis_connected():
                return f(*args, **kwargs)
            
            # Tạo cache key từ request
            cache_key = generate_cache_key(key_prefix, request)
            
            # Thử lấy từ cache
            cached_response = redis_helper.get(cache_key)
            if cached_response is not None:
                # Trả về response từ cache
                return current_app.response_class(
                    response=json.dumps(cached_response),
                    status=200,
                    mimetype='application/json'
                )
            
            # Gọi hàm gốc
            response = f(*args, **kwargs)
            
            # Lưu response vào cache nếu thành công
            try:
                if response.status_code == 200:
                    response_data = response.get_json()
                    if response_data:
                        redis_helper.set(cache_key, response_data, expire=ttl)
            except:
                pass  # Không lưu cache nếu có lỗi
            
            return response
        
        return decorated_function
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator để xóa cache khi có thay đổi dữ liệu
    
    Args:
        pattern: Pattern để xác định cache keys cần xóa
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Gọi hàm gốc
            response = f(*args, **kwargs)
            
            # Xóa cache nếu Redis đã kết nối
            if is_redis_connected():
                try:
                    # Tìm và xóa tất cả keys matching pattern
                    keys_to_delete = redis_helper.keys(f"{pattern}*")
                    for key in keys_to_delete:
                        redis_helper.delete(key)
                except:
                    pass  # Bỏ qua lỗi khi xóa cache
            
            return response
        
        return decorated_function
    return decorator


def generate_cache_key(prefix: str, req) -> str:
    """
    Tạo cache key từ request
    
    Args:
        prefix: Key prefix
        req: Flask request object
    
    Returns:
        str: Cache key
    """
    # Tạo hash từ URL và query parameters
    key_data = {
        'method': req.method,
        'path': req.path,
        'args': dict(req.args),
        'data': req.get_data(as_text=True) if req.method in ['POST', 'PUT', 'PATCH'] else ''
    }
    
    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"{prefix}:{key_hash}"


class RedisCacheManager:
    """Manager class for Redis cache operations"""
    
    @staticmethod
    def cache_user_data(user_id: int, user_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache user data
        
        Args:
            user_id: User ID
            user_data: User data to cache
            ttl: Time to live in seconds
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        key = f"user:{user_id}"
        return redis_helper.set(key, user_data, expire=ttl)
    
    @staticmethod
    def get_cached_user(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached user data
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[Dict[str, Any]]: Cached user data or None
        """
        if not is_redis_connected():
            return None
        
        key = f"user:{user_id}"
        return redis_helper.get(key)
    
    @staticmethod
    def invalidate_user_cache(user_id: int) -> bool:
        """
        Invalidate user cache
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        key = f"user:{user_id}"
        return redis_helper.delete(key)
    
    @staticmethod
    def cache_session(session_id: str, session_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """
        Cache session data
        
        Args:
            session_id: Session ID
            session_data: Session data to cache
            ttl: Time to live in seconds (default: 24 hours)
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        key = f"session:{session_id}"
        return redis_helper.set(key, session_data, expire=ttl)
    
    @staticmethod
    def get_cached_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached session data
        
        Args:
            session_id: Session ID
        
        Returns:
            Optional[Dict[str, Any]]: Cached session data or None
        """
        if not is_redis_connected():
            return None
        
        key = f"session:{session_id}"
        return redis_helper.get(key)
    
    @staticmethod
    def invalidate_session_cache(session_id: str) -> bool:
        """
        Invalidate session cache
        
        Args:
            session_id: Session ID
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        key = f"session:{session_id}"
        return redis_helper.delete(key)
    
    @staticmethod
    def add_to_blacklist(token: str, ttl: int = 3600) -> bool:
        """
        Add token to blacklist
        
        Args:
            token: JWT token
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        key = f"blacklist:{token}"
        return redis_helper.set(key, "blacklisted", expire=ttl)
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Check if token is blacklisted
        
        Args:
            token: JWT token
        
        Returns:
            bool: True if token is blacklisted
        """
        if not is_redis_connected():
            return False
        
        key = f"blacklist:{token}"
        return redis_helper.exists(key)
    
    @staticmethod
    def cache_api_response(endpoint: str, params: Dict[str, Any], 
                          response_data: Dict[str, Any], ttl: int = 300) -> bool:
        """
        Cache API response
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            response_data: Response data to cache
            ttl: Time to live in seconds (default: 5 minutes)
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        # Tạo key từ endpoint và params
        key_data = {'endpoint': endpoint, 'params': params}
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        key = f"api:{endpoint}:{key_hash}"
        return redis_helper.set(key, response_data, expire=ttl)
    
    @staticmethod
    def get_cached_api_response(endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached API response
        
        Args:
            endpoint: API endpoint
            params: Request parameters
        
        Returns:
            Optional[Dict[str, Any]]: Cached response or None
        """
        if not is_redis_connected():
            return None
        
        # Tạo key từ endpoint và params
        key_data = {'endpoint': endpoint, 'params': params}
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        key = f"api:{endpoint}:{key_hash}"
        return redis_helper.get(key)
    
    @staticmethod
    def invalidate_api_cache(endpoint_pattern: str) -> bool:
        """
        Invalidate API cache by pattern
        
        Args:
            endpoint_pattern: Pattern to match cache keys
        
        Returns:
            bool: True if successful
        """
        if not is_redis_connected():
            return False
        
        try:
            keys_to_delete = redis_helper.keys(f"api:{endpoint_pattern}*")
            for key in keys_to_delete:
                redis_helper.delete(key)
            return True
        except:
            return False


# Create instance for easy import
redis_cache = RedisCacheManager()