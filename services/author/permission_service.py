from database import db
from models.permission import Permission
from models.role_permission import RolePermission
from models.user_role import UserRole
from models.role import Role
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode

class PermissionService:
    @staticmethod
    def list_permissions():
        perms = Permission.query.all()
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
        return response_success({"id": perm_id}, key="deleted")

    @staticmethod
    def assign_permission(role_id: int, perm_id: int):
        role = Role.query.get(role_id)
        perm = Permission.query.get(perm_id)
        if not role or not perm:
            return response_error("Role or Permission not found", HttpCode.not_found)

        if perm not in role.permissions:
            role.permissions.append(perm)
            db.session.commit()
        return response_success(role.to_dict(), key="role")

    @staticmethod
    def remove_permission(role_id: int, perm_id: int):
        role = Role.query.get(role_id)
        perm = Permission.query.get(perm_id)
        if not role or not perm:
            return response_error("Role or Permission not found", HttpCode.not_found)

        if perm in role.permissions:
            role.permissions.remove(perm)
            db.session.commit()
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