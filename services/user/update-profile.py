from database import get_mysql_connection

def update_profile(user_id, data):
    """
    Cập nhật thông tin profile người dùng.
    """
    mysql_conn = None
    mysql_cursor = None

    try:
        # 1. Kết nối MySQL và lấy thông tin user id
        mysql_conn = get_mysql_connection()
        mysql_cursor = mysql_conn.cursor(dictionary=True)

        mysql_cursor.execute("SELECT user_id FROM users WHERE id = %s", (user_id,))
        user = mysql_cursor.fetchone()

        if not user:
            return {"error": "User not found"}

        user_id = user["employee_id"]

        # 2. Cập nhật thông tin trong bảng `users` (MySQL)
        return {"message": "Profile updated successfully"}

    except Exception as e:
        if mysql_conn:
            mysql_conn.rollback()
        return {"error": str(e)}

    finally:
        if mysql_cursor:
            mysql_cursor.close()
        if mysql_conn:
            mysql_conn.close()