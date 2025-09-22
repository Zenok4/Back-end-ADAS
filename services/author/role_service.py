from database import db
from models.role import Role
from models.user_role import UserRole
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode


class RoleService:

    @staticmethod
    def list_roles():
        try:
            roles = Role.query.all()
            return response_success([r.to_dict() for r in roles], key="roles")
        except Exception as e:
            return response_error(f"Failed to list roles: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def get_role_by_id(role_id: int):
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)
            return response_success(role.to_dict(), key="role")
        except Exception as e:
            return response_error(f"Failed to get role: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def get_role_by_name(name: str):
        try:
            role = Role.query.filter_by(name=name).first()
            if not role:
                return response_error("Role not found", HttpCode.not_found)
            return response_success(role.to_dict(), key="role")
        except Exception as e:
            return response_error(f"Failed to get role: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def create_role(name: str, description: str = None):
        try:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.commit()
            return response_success(role.to_dict(), key="role", message="Role created", code=HttpCode.created)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Create role failed: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def update_role(role_id: int, **kwargs):
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)

            for key, value in kwargs.items():
                if hasattr(role, key):  # tránh set field không hợp lệ
                    setattr(role, key, value)

            db.session.commit()
            return response_success(role.to_dict(), key="role", message="Role updated")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def delete_role(role_id: int):
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)

            db.session.delete(role)
            db.session.commit()
            return response_success({"id": role_id}, key="deleted", message="Role deleted")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Delete failed: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def get_user_roles(user_id: int):
        """
        Trả về danh sách role mà user có.
        """
        try:
            roles = (
                db.session.query(Role)
                .join(UserRole, UserRole.role_id == Role.id)
                .filter(UserRole.user_id == user_id)
                .all()
            )
            return response_success([r.to_dict() for r in roles], key="roles")
        except Exception as e:
            return response_error(f"Failed to get user roles: {str(e)}", HttpCode.internal_server_error)
