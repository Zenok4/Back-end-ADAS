from database import db
from middlewares.permission_required import clear_permissions_cache
from models.permission import Permission
from models.role_permission import RolePermission
from models.user_role import UserRole
from models.role import Role
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode
from services.audit_log_service import AuditLogService

class PermissionService:
    @staticmethod
    def list_permissions():
        perms = Permission.query.all()
        print(">>> perms:", perms)
        return response_success([p.to_dict() for p in perms], key="permissions")

    @staticmethod
    def get_permission_by_id(perm_id: int):
        perm = Permission.query.get(perm_id)
        if not perm:
            return response_error("Permission not found", HttpCode.not_found)
        return response_success(perm.to_dict(), key="permission")

    @staticmethod
    def get_permission_by_code(code: str):
        perm = Permission.query.filter_by(code=code).first()
        if not perm:
            return response_error("Permission not found", HttpCode.not_found)
        return response_success(perm.to_dict(), key="permission")

    @staticmethod
    def create_permission(code: str, title: str, description: str = None, group_id: int = None):
        perm = Permission(code=code, title=title, description=description, group_id=group_id)
        db.session.add(perm)
        db.session.commit()
        AuditLogService.log_action(user_id=None, action="CREATE", object_type="PERMISSION", object_id=perm.id)
        return response_success(perm.to_dict(), key="permission")

    @staticmethod
    def update_permission(perm_id: int, **kwargs):
        perm = Permission.query.get(perm_id)
        if not perm:
            return response_error("Permission not found", HttpCode.not_found)
        for key, value in kwargs.items():
            if hasattr(perm, key):  # tránh set field không hợp lệ
                setattr(perm, key, value)
        try:
            db.session.commit()
            AuditLogService.log_action(user_id=None, action="UPDATE", object_type="PERMISSION", object_id=perm.id)
            return response_success(perm.to_dict(), key="permission")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def delete_permission(perm_id: int):
        perm = Permission.query.get(perm_id)
        if not perm:
            return response_error("Permission not found", HttpCode.not_found)
        db.session.delete(perm)
        db.session.commit()
        AuditLogService.log_action(user_id=None, action="DELETE", object_type="PERMISSION", object_id=perm_id)
        return response_success({"id": perm_id}, key="deleted")

    @staticmethod
    def assign_permissions(role_id: int, perm_ids: list[int]):
        """
        Gán nhiều permissions cho 1 role.
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)
            
            new_permissions = []
            if perm_ids:
                unique_perm_ids = list(set(perm_ids))
                new_permissions = Permission.query.filter(Permission.id.in_(unique_perm_ids)).all()

            if len(new_permissions) != len(set(unique_perm_ids)):
                print(f"Warning: Some permission IDs in {unique_perm_ids} were not found.")

            role.permissions = new_permissions
            db.session.commit()
            clear_permissions_cache()
            AuditLogService.log_action(user_id=None, action="ASSIGN_PERMISSIONS", object_type="ROLE", object_id=role_id, new_values={"permissions": perm_ids})
            return response_success(
                [p.to_dict() for p in new_permissions],
                key="assigned_permissions",
                message="Permissions assigned successfully"
            )

        except Exception as e:
            db.session.rollback()
            print(f"Error in assign_permissions: {str(e)}")
            return response_error(f"Failed to assign permissions: {str(e)}", HttpCode.internal_server_error)


    @staticmethod
    def remove_permission(role_id: int, perm_id: int):
        role = Role.query.get(role_id)
        perm = Permission.query.get(perm_id)
        if not role or not perm:
            return response_error("Role or Permission not found", HttpCode.not_found)

        if perm in role.permissions:
            role.permissions.remove(perm)
            db.session.commit()
            clear_permissions_cache()
        return response_success(role.to_dict(), key="role")

    @staticmethod
    def get_user_permissions(user_id: int):
        rows = (
            db.session.query(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .distinct()
            .all()
        )
        return response_success([r.to_dict() for r in rows], key="permissions")
    
    @staticmethod
    def assign_role_to_user(user_id: int, role_id: int):
        """
        Gán role cho user (thêm bản ghi vào bảng user_roles).
        """
        try:
            # Kiểm tra role tồn tại
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)

            # Kiểm tra đã tồn tại binding chưa
            exists = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
            if exists:
                return response_error("User already has this role", HttpCode.conflict)

            binding = UserRole(user_id=user_id, role_id=role_id)
            db.session.add(binding)
            db.session.commit()
            clear_permissions_cache()
            AuditLogService.log_action(user_id=user_id, action="ASSIGN_ROLE", object_type="USER", object_id=user_id, new_values={"role_id": role_id})
            return response_success(
                {"user_id": user_id, "role_id": role_id},
                message="Role assigned to user",
                code=HttpCode.created,
            )
        except Exception as e:
            db.session.rollback()
            return response_error(f"Assign role failed: {str(e)}", HttpCode.internal_server_error)