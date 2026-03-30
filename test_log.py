from app import app
from services.audit_log_service import AuditLogService

with app.app_context():
    AuditLogService.log_action(
        user_id=1,
        action="TEST_ACTION",
        object_type="TEST_TYPE",
        object_id="999",
        old_values={"data": "old"},
        new_values={"data": "new"},
        session_id="test-session-123"
    )
    print("Hoàn tất. Hãy kiểm tra bảng audit_logs trong Database.")