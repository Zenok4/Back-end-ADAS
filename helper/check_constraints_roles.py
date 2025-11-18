from flask_jwt_extended import get_jwt_identity

from models.user import User


def get_current_user_highest_level():
    """
    Lấy level cao nhất của user đang đăng nhập từ JWT token.
    """
    try:
        # Lấy user_id từ token 
        user_id = get_jwt_identity() 
        # Nếu không có user_id (ví dụ: token không hợp lệ, hoặc không có token)
        if not user_id:
            return 0
        
        user = User.query.get(int(user_id))
        
        # - 'not user': Nếu user_id trong token nhưng không (còn) tồn tại trong DB.
        # - 'not user.roles': Nếu user tồn tại, nhưng danh sách vai trò (relationship) của họ bị rỗng.
        if not user or not user.roles:
            return 0 
        
        # Tìm level cao nhất từ danh sách roles của user
        highest_level = max(role.level for role in user.roles)
        return highest_level
    except Exception:
        return 0

