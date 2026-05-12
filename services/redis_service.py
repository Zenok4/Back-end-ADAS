"""
Redis Service
Service layer để quản lý Redis operations cho ứng dụng
"""

import json
import time
from typing import Any, Optional, Dict, List, Union
from config import is_redis_connected
from helper.redis_helper import redis_helper
from middlewares.redis_cache_middleware import redis_cache


class RedisService:
    """Service class for Redis operations"""
    
    @staticmethod
    def health_check() -> Dict[str, Any]:
        """
        Kiểm tra sức khỏe Redis connection
        
        Returns:
            Dict[str, Any]: Health check results
        """
        if not is_redis_connected():
            return {
                "status": "down",
                "message": "Redis not connected",
                "timestamp": time.time()
            }
        
        try:
            # Test ping
            start_time = time.time()
            redis_helper.get("health_check")
            ping_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Get Redis info
            info = {
                "status": "up",
                "ping_time_ms": round(ping_time, 2),
                "timestamp": time.time(),
                "connected": True
            }
            
            return info
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
    
    @staticmethod
    def cache_user_session(user_id: int, session_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """
        Cache user session data
        
        Args:
            user_id: User ID
            session_data: Session data
            ttl: Time to live in seconds (default: 24 hours)
        
        Returns:
            bool: True if successful
        """
        return redis_cache.cache_session(f"user:{user_id}:session", session_data, ttl)
    
    @staticmethod
    def get_user_session(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached user session
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[Dict[str, Any]]: Session data or None
        """
        return redis_cache.get_cached_session(f"user:{user_id}:session")
    
    @staticmethod
    def invalidate_user_session(user_id: int) -> bool:
        """
        Invalidate user session cache
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if successful
        """
        return redis_cache.invalidate_session_cache(f"user:{user_id}:session")
    
    @staticmethod
    def cache_user_permissions(user_id: int, permissions: List[str], ttl: int = 3600) -> bool:
        """
        Cache user permissions
        
        Args:
            user_id: User ID
            permissions: List of permissions
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            bool: True if successful
        """
        key = f"user:{user_id}:permissions"
        return redis_helper.set(key, permissions, expire=ttl)
    
    @staticmethod
    def get_user_permissions(user_id: int) -> Optional[List[str]]:
        """
        Get cached user permissions
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[List[str]]: Permissions or None
        """
        key = f"user:{user_id}:permissions"
        return redis_helper.get(key)
    
    @staticmethod
    def cache_detection_result(detection_type: str, detection_id: str, 
                              result: Dict[str, Any], ttl: int = 1800) -> bool:
        """
        Cache detection result
        
        Args:
            detection_type: Type of detection (sign, lane, object, drowsy)
            detection_id: Detection ID
            result: Detection result
            ttl: Time to live in seconds (default: 30 minutes)
        
        Returns:
            bool: True if successful
        """
        key = f"detection:{detection_type}:{detection_id}"
        return redis_helper.set(key, result, expire=ttl)
    
    @staticmethod
    def get_detection_result(detection_type: str, detection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached detection result
        
        Args:
            detection_type: Type of detection
            detection_id: Detection ID
        
        Returns:
            Optional[Dict[str, Any]]: Detection result or None
        """
        key = f"detection:{detection_type}:{detection_id}"
        return redis_helper.get(key)
    
    @staticmethod
    def cache_trip_data(trip_id: str, trip_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """
        Cache trip data
        
        Args:
            trip_id: Trip ID
            trip_data: Trip data
            ttl: Time to live in seconds (default: 2 hours)
        
        Returns:
            bool: True if successful
        """
        key = f"trip:{trip_id}"
        return redis_helper.set(key, trip_data, expire=ttl)
    
    @staticmethod
    def get_trip_data(trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached trip data
        
        Args:
            trip_id: Trip ID
        
        Returns:
            Optional[Dict[str, Any]]: Trip data or None
        """
        key = f"trip:{trip_id}"
        return redis_helper.get(key)
    
    @staticmethod
    def cache_statistics(stat_type: str, data: Dict[str, Any], ttl: int = 300) -> bool:
        """
        Cache statistics data
        
        Args:
            stat_type: Type of statistics
            data: Statistics data
            ttl: Time to live in seconds (default: 5 minutes)
        
        Returns:
            bool: True if successful
        """
        key = f"stats:{stat_type}"
        return redis_helper.set(key, data, expire=ttl)
    
    @staticmethod
    def get_statistics(stat_type: str) -> Optional[Dict[str, Any]]:
        """
        Get cached statistics
        
        Args:
            stat_type: Type of statistics
        
        Returns:
            Optional[Dict[str, Any]]: Statistics data or None
        """
        key = f"stats:{stat_type}"
        return redis_helper.get(key)
    
    @staticmethod
    def rate_limit(key: str, limit: int, window: int) -> bool:
        """
        Rate limiting với Redis
        
        Args:
            key: Rate limit key
            limit: Số request tối đa
            window: Thời gian window (giây)
        
        Returns:
            bool: True nếu vượt quá limit, False nếu OK
        """
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
    
    @staticmethod
    def get_rate_limit_info(key: str) -> Dict[str, Any]:
        """
        Get rate limit information
        
        Args:
            key: Rate limit key
        
        Returns:
            Dict[str, Any]: Rate limit information
        """
        current = redis_helper.get(key)
        ttl = redis_helper.ttl(key)
        
        return {
            "current_count": int(current) if current else 0,
            "ttl": ttl,
            "key": key
        }
    
    @staticmethod
    def cache_ai_model_result(model_name: str, input_hash: str, 
                             result: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache AI model result
        
        Args:
            model_name: AI model name
            input_hash: Hash of input data
            result: Model result
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            bool: True if successful
        """
        key = f"ai:{model_name}:{input_hash}"
        return redis_helper.set(key, result, expire=ttl)
    
    @staticmethod
    def get_ai_model_result(model_name: str, input_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached AI model result
        
        Args:
            model_name: AI model name
            input_hash: Hash of input data
        
        Returns:
            Optional[Dict[str, Any]]: Model result or None
        """
        key = f"ai:{model_name}:{input_hash}"
        return redis_helper.get(key)
    
    @staticmethod
    def cache_config(config_key: str, config_value: Any, ttl: int = 86400) -> bool:
        """
        Cache configuration
        
        Args:
            config_key: Configuration key
            config_value: Configuration value
            ttl: Time to live in seconds (default: 24 hours)
        
        Returns:
            bool: True if successful
        """
        key = f"config:{config_key}"
        return redis_helper.set(key, config_value, expire=ttl)
    
    @staticmethod
    def get_config(config_key: str, default: Any = None) -> Any:
        """
        Get cached configuration
        
        Args:
            config_key: Configuration key
            default: Default value if not found
        
        Returns:
            Any: Configuration value or default
        """
        key = f"config:{config_key}"
        return redis_helper.get(key, default)
    
    @staticmethod
    def get_redis_stats() -> Dict[str, Any]:
        """
        Get Redis statistics
        
        Returns:
            Dict[str, Any]: Redis statistics
        """
        if not is_redis_connected():
            return {"error": "Redis not connected"}
        
        try:
            # Get keys count by pattern
            patterns = ["user:*", "session:*", "detection:*", "trip:*", "stats:*", "ai:*", "config:*"]
            key_counts = {}
            
            for pattern in patterns:
                keys = redis_helper.keys(pattern)
                key_counts[pattern] = len(keys)
            
            # Get memory info
            memory_info = {
                "total_keys": len(redis_helper.keys("*")),
                "key_counts": key_counts,
                "timestamp": time.time()
            }
            
            return memory_info
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def clear_cache_by_pattern(pattern: str) -> Dict[str, Any]:
        """
        Clear cache by pattern
        
        Args:
            pattern: Pattern to match keys
        
        Returns:
            Dict[str, Any]: Clear cache results
        """
        if not is_redis_connected():
            return {"error": "Redis not connected"}
        
        try:
            keys = redis_helper.keys(pattern)
            deleted_count = 0
            
            for key in keys:
                if redis_helper.delete(key):
                    deleted_count += 1
            
            return {
                "success": True,
                "pattern": pattern,
                "deleted_count": deleted_count,
                "total_keys": len(keys)
            }
        except Exception as e:
            return {"error": str(e)}


# Create instance for easy import
redis_service = RedisService()