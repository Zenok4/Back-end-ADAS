"""
Redis Production Configuration
Cấu hình Redis cho môi trường production
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RedisProductionConfig:
    """Redis configuration for production environment"""
    
    # Redis connection settings
    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = int(os.getenv("REDIS_PORT", 6379))
    PASSWORD = os.getenv("REDIS_PASSWORD", None)
    DB = int(os.getenv("REDIS_DB", 0))
    
    # Connection pool settings
    MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", 50))
    SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", 5))
    SOCKET_CONNECT_TIMEOUT = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", 5))
    RETRY_ON_TIMEOUT = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
    
    # SSL settings (for production with TLS)
    SSL = os.getenv("REDIS_SSL", "false").lower() == "true"
    SSL_CERT_REQS = os.getenv("REDIS_SSL_CERT_REQS", "required")  # none, optional, required
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", 30))
    
    # Cache TTL settings (in seconds)
    CACHE_TTL = {
        "USER_DATA": int(os.getenv("REDIS_TTL_USER_DATA", 3600)),  # 1 hour
        "USER_SESSION": int(os.getenv("REDIS_TTL_USER_SESSION", 86400)),  # 24 hours
        "USER_PERMISSIONS": int(os.getenv("REDIS_TTL_USER_PERMISSIONS", 1800)),  # 30 minutes
        "API_RESPONSE": int(os.getenv("REDIS_TTL_API_RESPONSE", 300)),  # 5 minutes
        "DETECTION_RESULT": int(os.getenv("REDIS_TTL_DETECTION_RESULT", 1800)),  # 30 minutes
        "TRIP_DATA": int(os.getenv("REDIS_TTL_TRIP_DATA", 7200)),  # 2 hours
        "STATISTICS": int(os.getenv("REDIS_TTL_STATISTICS", 300)),  # 5 minutes
        "AI_MODEL_RESULT": int(os.getenv("REDIS_TTL_AI_MODEL_RESULT", 3600)),  # 1 hour
        "CONFIGURATION": int(os.getenv("REDIS_TTL_CONFIGURATION", 86400)),  # 24 hours
        "BLACKLIST_TOKEN": int(os.getenv("REDIS_TTL_BLACKLIST_TOKEN", 3600)),  # 1 hour
    }
    
    # Rate limiting settings
    RATE_LIMIT = {
        "LOGIN_ATTEMPTS": int(os.getenv("RATE_LIMIT_LOGIN_ATTEMPTS", 5)),
        "LOGIN_WINDOW": int(os.getenv("RATE_LIMIT_LOGIN_WINDOW", 300)),  # 5 minutes
        "API_REQUESTS": int(os.getenv("RATE_LIMIT_API_REQUESTS", 100)),
        "API_WINDOW": int(os.getenv("RATE_LIMIT_API_WINDOW", 60)),  # 1 minute
        "REFRESH_TOKEN": int(os.getenv("RATE_LIMIT_REFRESH_TOKEN", 10)),
        "REFRESH_WINDOW": int(os.getenv("RATE_LIMIT_REFRESH_WINDOW", 300)),  # 5 minutes
    }
    
    @classmethod
    def get_redis_config(cls):
        """Get Redis connection configuration"""
        config = {
            "host": cls.HOST,
            "port": cls.PORT,
            "password": cls.PASSWORD,
            "db": cls.DB,
            "decode_responses": True,
            "socket_timeout": cls.SOCKET_TIMEOUT,
            "socket_connect_timeout": cls.SOCKET_CONNECT_TIMEOUT,
            "retry_on_timeout": cls.RETRY_ON_TIMEOUT,
            "max_connections": cls.MAX_CONNECTIONS,
        }
        
        # Add SSL configuration if enabled
        if cls.SSL:
            config.update({
                "ssl": True,
                "ssl_cert_reqs": cls.SSL_CERT_REQS,
            })
        
        return config
    
    @classmethod
    def get_cache_ttl(cls, cache_type: str) -> int:
        """Get TTL for cache type"""
        return cls.CACHE_TTL.get(cache_type.upper(), 300)  # Default 5 minutes
    
    @classmethod
    def get_rate_limit(cls, limit_type: str) -> tuple:
        """Get rate limit settings"""
        limit_key = f"{limit_type.upper()}_ATTEMPTS"
        window_key = f"{limit_type.upper()}_WINDOW"
        
        limit = cls.RATE_LIMIT.get(limit_key, 10)
        window = cls.RATE_LIMIT.get(window_key, 60)
        
        return limit, window


# Example environment variables for production
EXAMPLE_ENV = """
# Redis Production Configuration
REDIS_HOST=redis-production.example.com
REDIS_PORT=6379
REDIS_PASSWORD=your_strong_password_here
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true

# SSL/TLS (enable for production)
REDIS_SSL=true
REDIS_SSL_CERT_REQS=required

# Cache TTL (seconds)
REDIS_TTL_USER_DATA=3600
REDIS_TTL_USER_SESSION=86400
REDIS_TTL_USER_PERMISSIONS=1800
REDIS_TTL_API_RESPONSE=300
REDIS_TTL_DETECTION_RESULT=1800
REDIS_TTL_TRIP_DATA=7200
REDIS_TTL_STATISTICS=300
REDIS_TTL_AI_MODEL_RESULT=3600
REDIS_TTL_CONFIGURATION=86400
REDIS_TTL_BLACKLIST_TOKEN=3600

# Rate Limiting
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=300
RATE_LIMIT_API_REQUESTS=100
RATE_LIMIT_API_WINDOW=60
RATE_LIMIT_REFRESH_TOKEN=10
RATE_LIMIT_REFRESH_WINDOW=300
"""


def print_production_config():
    """Print production configuration example"""
    print("=== Redis Production Configuration ===")
    print("\n1. Add these environment variables to your .env file:")
    print(EXAMPLE_ENV)
    
    print("\n2. Update config.py to use production config:")
    print("""
# In config.py, replace REDIS_CONFIG with:
from redis_production_config import RedisProductionConfig

REDIS_CONFIG = RedisProductionConfig.get_redis_config()
    """)
    
    print("\n3. Example usage:")
    print("""
from redis_production_config import RedisProductionConfig

# Get TTL for user data
ttl = RedisProductionConfig.get_cache_ttl("USER_DATA")

# Get rate limit for login
limit, window = RedisProductionConfig.get_rate_limit("LOGIN")
    """)


if __name__ == "__main__":
    print_production_config()