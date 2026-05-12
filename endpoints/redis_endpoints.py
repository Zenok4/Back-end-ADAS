"""
Redis Management Endpoints
API endpoints để quản lý và monitor Redis
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.redis_service import redis_service
from helper.normalization_response import response_success, response_error
from type.http_constants import HttpCode
from config import is_redis_connected

redis_bp = Blueprint("redis_bp", __name__, url_prefix="/redis")


@redis_bp.route("/health", methods=["GET"])
def redis_health():
    """
    Kiểm tra sức khỏe Redis connection
    
    Returns:
        JSON: Health check results
    """
    health_info = redis_service.health_check()
    
    if health_info.get("status") == "up":
        return jsonify(response_success(
            data=health_info,
            message="Redis is healthy",
            code=HttpCode.success
        )), HttpCode.success
    else:
        return jsonify(response_error(
            message="Redis is not healthy",
            data=health_info,
            code=HttpCode.service_unavailable
        )), HttpCode.service_unavailable


@redis_bp.route("/stats", methods=["GET"])
@jwt_required()
def redis_stats():
    """
    Lấy thống kê Redis
    
    Returns:
        JSON: Redis statistics
    """
    stats = redis_service.get_redis_stats()
    
    if "error" in stats:
        return jsonify(response_error(
            message=stats["error"],
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error
    
    return jsonify(response_success(
        data=stats,
        message="Redis statistics retrieved",
        code=HttpCode.success
    )), HttpCode.success


@redis_bp.route("/cache/clear", methods=["POST"])
@jwt_required()
def clear_cache():
    """
    Xóa cache theo pattern
    
    Body:
        {
            "pattern": "user:*"  # Pattern để xóa cache
        }
    
    Returns:
        JSON: Clear cache results
    """
    data = request.get_json(silent=True) or {}
    pattern = data.get("pattern", "*")
    
    if not pattern:
        return jsonify(response_error(
            message="Pattern is required",
            code=HttpCode.bad_request
        )), HttpCode.bad_request
    
    result = redis_service.clear_cache_by_pattern(pattern)
    
    if "error" in result:
        return jsonify(response_error(
            message=result["error"],
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error
    
    return jsonify(response_success(
        data=result,
        message=f"Cache cleared for pattern: {pattern}",
        code=HttpCode.success
    )), HttpCode.success


@redis_bp.route("/cache/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
def clear_user_cache(user_id: int):
    """
    Xóa cache của user cụ thể
    
    Args:
        user_id: User ID
    
    Returns:
        JSON: Clear cache results
    """
    # Xóa các cache liên quan đến user
    patterns = [
        f"user:{user_id}:*",
        f"session:user:{user_id}:*"
    ]
    
    results = []
    for pattern in patterns:
        result = redis_service.clear_cache_by_pattern(pattern)
        results.append({
            "pattern": pattern,
            "result": result
        })
    
    return jsonify(response_success(
        data={"results": results},
        message=f"User cache cleared for user_id: {user_id}",
        code=HttpCode.success
    )), HttpCode.success


@redis_bp.route("/rate-limit/<key>", methods=["GET"])
@jwt_required()
def get_rate_limit_info(key: str):
    """
    Lấy thông tin rate limit
    
    Args:
        key: Rate limit key
    
    Returns:
        JSON: Rate limit information
    """
    info = redis_service.get_rate_limit_info(key)
    
    return jsonify(response_success(
        data=info,
        message="Rate limit information retrieved",
        code=HttpCode.success
    )), HttpCode.success


@redis_bp.route("/test/cache", methods=["POST"])
@jwt_required()
def test_cache():
    """
    Test cache operations
    
    Body:
        {
            "key": "test_key",
            "value": "test_value",
            "ttl": 60
        }
    
    Returns:
        JSON: Test results
    """
    data = request.get_json(silent=True) or {}
    key = data.get("key", "test_key")
    value = data.get("value", "test_value")
    ttl = data.get("ttl", 60)
    
    if not is_redis_connected():
        return jsonify(response_error(
            message="Redis not connected",
            code=HttpCode.service_unavailable
        )), HttpCode.service_unavailable
    
    # Test set
    set_result = redis_service.cache_config(key, value, ttl)
    
    # Test get
    get_result = redis_service.get_config(key)
    
    # Test delete
    delete_result = redis_service.clear_cache_by_pattern(key)
    
    return jsonify(response_success(
        data={
            "set_result": set_result,
            "get_result": get_result,
            "delete_result": delete_result,
            "key": key,
            "value": value,
            "ttl": ttl
        },
        message="Cache test completed",
        code=HttpCode.success
    )), HttpCode.success


@redis_bp.route("/patterns", methods=["GET"])
@jwt_required()
def get_cache_patterns():
    """
    Lấy danh sách cache patterns phổ biến
    
    Returns:
        JSON: List of cache patterns
    """
    patterns = {
        "user_data": "user:*",
        "user_sessions": "session:user:*",
        "user_permissions": "user:*:permissions",
        "detection_results": "detection:*",
        "trip_data": "trip:*",
        "statistics": "stats:*",
        "ai_model_results": "ai:*",
        "configurations": "config:*",
        "blacklisted_tokens": "blacklist:*",
        "api_cache": "api:*"
    }
    
    return jsonify(response_success(
        data=patterns,
        message="Cache patterns retrieved",
        code=HttpCode.success
    )), HttpCode.success


@redis_bp.route("/memory", methods=["GET"])
@jwt_required()
def get_memory_info():
    """
    Lấy thông tin memory usage (ước tính)
    
    Returns:
        JSON: Memory information
    """
    if not is_redis_connected():
        return jsonify(response_error(
            message="Redis not connected",
            code=HttpCode.service_unavailable
        )), HttpCode.service_unavailable
    
    try:
        # Get total keys
        total_keys = len(redis_service.get_redis_stats().get("total_keys", 0))
        
        # Estimate memory usage (rough estimate)
        # Giả sử mỗi key-value pair tốn khoảng 100 bytes
        estimated_memory_kb = (total_keys * 100) / 1024
        
        memory_info = {
            "total_keys": total_keys,
            "estimated_memory_kb": round(estimated_memory_kb, 2),
            "estimated_memory_mb": round(estimated_memory_kb / 1024, 2),
            "note": "Memory estimation is approximate"
        }
        
        return jsonify(response_success(
            data=memory_info,
            message="Memory information retrieved",
            code=HttpCode.success
        )), HttpCode.success
    except Exception as e:
        return jsonify(response_error(
            message=f"Failed to get memory info: {str(e)}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error