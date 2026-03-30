from database import db
from models.audit_log import AuditLog
from flask import request
import logging

logger = logging.getLogger("backend")

class AuditLogService:
    @staticmethod
    def log_action(user_id, action, object_type, object_id, old_values=None, new_values=None, session_id=None, meta_data=None):
        try:
            # Lấy IP và User-Agent từ Flask request context nếu có
            ip = request.remote_addr if request else None
            user_agent = request.headers.get("User-Agent") if request else None

            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                object_type=object_type,
                object_id=str(object_id),
                old_values=old_values,
                new_values=new_values,
                ip=ip,
                user_agent=user_agent,
                session_id=session_id,
                meta_data=meta_data
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi ghi DB log: {str(e)}")