"""
Redis Helper Module
Cung cấp các hàm tiện ích để làm việc với Redis
"""

import json
import pickle
from typing import Any, Optional, Union, List, Dict
import redis
from config import redis_client


class RedisHelper:
    """Helper class for Redis operations"""
    
    @staticmethod
    def set(key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis
        
        Args:
            key: Redis key
            value: Value to store (will be serialized)
            expire: Expiration time in seconds (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not redis_client:
            return False
            
        try:
            # Serialize value based on type
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
                
            if expire:
                return redis_client.setex(key, expire, serialized_value)
            else:
                return redis_client.set(key, serialized_value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get a value from Redis
        
        Args:
            key: Redis key
            default: Default value if key doesn't exist
            
        Returns:
            Any: Deserialized value or default
        """
        if not redis_client:
            return default
            
        try:
            value = redis_client.get(key)
            if value is None:
                return default
                
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Return as string if not JSON
                return value.decode('utf-8') if isinstance(value, bytes) else value
        except Exception as e:
            print(f"Redis get error: {e}")
            return default
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete a key from Redis
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not redis_client:
            return False
            
        try:
            return redis_client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    def exists(key: str) -> bool:
        """
        Check if a key exists in Redis
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if key exists
        """
        if not redis_client:
            return False
            
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    @staticmethod
    def expire(key: str, seconds: int) -> bool:
        """
        Set expiration time for a key
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        if not redis_client:
            return False
            
        try:
            return redis_client.expire(key, seconds)
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False
    
    @staticmethod
    def ttl(key: str) -> int:
        """
        Get time to live for a key
        
        Args:
            key: Redis key
            
        Returns:
            int: TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        if not redis_client:
            return -2
            
        try:
            return redis_client.ttl(key)
        except Exception as e:
            print(f"Redis ttl error: {e}")
            return -2
    
    @staticmethod
    def keys(pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern
        
        Args:
            pattern: Pattern to match (default: "*")
            
        Returns:
            List[str]: List of matching keys
        """
        if not redis_client:
            return []
            
        try:
            return [key.decode('utf-8') if isinstance(key, bytes) else key 
                   for key in redis_client.keys(pattern)]
        except Exception as e:
            print(f"Redis keys error: {e}")
            return []
    
    @staticmethod
    def flush_all() -> bool:
        """
        Flush all Redis data
        
        Returns:
            bool: True if successful
        """
        if not redis_client:
            return False
            
        try:
            return redis_client.flushall()
        except Exception as e:
            print(f"Redis flushall error: {e}")
            return False
    
    @staticmethod
    def increment(key: str, amount: int = 1) -> int:
        """
        Increment a counter
        
        Args:
            key: Redis key
            amount: Amount to increment (default: 1)
            
        Returns:
            int: New value after increment
        """
        if not redis_client:
            return 0
            
        try:
            return redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Redis increment error: {e}")
            return 0
    
    @staticmethod
    def decrement(key: str, amount: int = 1) -> int:
        """
        Decrement a counter
        
        Args:
            key: Redis key
            amount: Amount to decrement (default: 1)
            
        Returns:
            int: New value after decrement
        """
        if not redis_client:
            return 0
            
        try:
            return redis_client.decrby(key, amount)
        except Exception as e:
            print(f"Redis decrement error: {e}")
            return 0
    
    @staticmethod
    def hash_set(hash_name: str, key: str, value: Any) -> bool:
        """
        Set field in hash
        
        Args:
            hash_name: Hash name
            key: Field key
            value: Field value
            
        Returns:
            bool: True if successful
        """
        if not redis_client:
            return False
            
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
                
            return redis_client.hset(hash_name, key, serialized_value) > 0
        except Exception as e:
            print(f"Redis hash_set error: {e}")
            return False
    
    @staticmethod
    def hash_get(hash_name: str, key: str, default: Any = None) -> Any:
        """
        Get field from hash
        
        Args:
            hash_name: Hash name
            key: Field key
            default: Default value if field doesn't exist
            
        Returns:
            Any: Field value or default
        """
        if not redis_client:
            return default
            
        try:
            value = redis_client.hget(hash_name, key)
            if value is None:
                return default
                
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8') if isinstance(value, bytes) else value
        except Exception as e:
            print(f"Redis hash_get error: {e}")
            return default
    
    @staticmethod
    def hash_get_all(hash_name: str) -> Dict[str, Any]:
        """
        Get all fields from hash
        
        Args:
            hash_name: Hash name
            
        Returns:
            Dict[str, Any]: All fields and values
        """
        if not redis_client:
            return {}
            
        try:
            result = redis_client.hgetall(hash_name)
            decoded_result = {}
            for key, value in result.items():
                k = key.decode('utf-8') if isinstance(key, bytes) else key
                try:
                    v = json.loads(value)
                except json.JSONDecodeError:
                    v = value.decode('utf-8') if isinstance(value, bytes) else value
                decoded_result[k] = v
            return decoded_result
        except Exception as e:
            print(f"Redis hash_get_all error: {e}")
            return {}


# Create instance for easy import
redis_helper = RedisHelper()