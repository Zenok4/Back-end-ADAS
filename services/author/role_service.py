from database import db
from models.role import Role
from models.user_role import UserRole
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode


class RoleService:

    # =============== LIST ALL ROLES ===============
    @staticmethod
    def list_roles(list_perm: bool = False):
        try:
            roles = Role.query.all()
            if not roles:
                return response_success({"roles": []}, message="No roles found", code=HttpCode.success)

            data = [r.to_dict(include_permissions=list_perm) for r in roles]
            return response_success({"roles": data}, message="List roles successfully", code=HttpCode.success)
        except Exception as e:
            return response_error(f"Failed to list roles: {str(e)}", HttpCode.internal_server_error)


    # =============== GET ROLE BY ID ===============
    @staticmethod
    def get_role_by_id(role_id: int, include_permissions: bool = False):
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.success)

            return response_success(
                role.to_dict(include_permissions=include_permissions),
                key="role",
                message="Get role successfully"
            )
        except Exception as e:
            return response_error(f"Failed to get role: {str(e)}", HttpCode.internal_server_error)


    # =============== GET ROLE BY NAME ===============
    @staticmethod
    def get_role_by_name(name: str, include_permissions: bool = False):
        try:
            role = Role.query.filter_by(name=name).first()
            if not role:
                return response_error("Role not found", HttpCode.success)

            return response_success(
                role.to_dict(include_permissions=include_permissions),
                key="role",
                message="Get role successfully"
            )
        except Exception as e:
            return response_error(f"Failed to get role: {str(e)}", HttpCode.internal_server_error)


    # =============== CREATE ROLE ===============
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


    # =============== UPDATE ROLE ===============
    @staticmethod
    def update_role(role_id: int, **kwargs):
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)

            for key, value in kwargs.items():
                if hasattr(role, key):
                    setattr(role, key, value)

            db.session.commit()
            return response_success(role.to_dict(), key="role", message="Role updated")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)


    # =============== DELETE ROLE ===============
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


    # =============== GET USER ROLES ===============
    @staticmethod
    def get_user_roles(user_id: int, include_permissions: bool = False):
        try:
            roles = (
                db.session.query(Role)
                .join(UserRole, UserRole.role_id == Role.id)
                .filter(UserRole.user_id == user_id)
                .all()
            )
            if not roles:
                return response_success([], key="roles", message="User has no roles")
            return response_success(
                [r.to_dict(include_permissions=include_permissions) for r in roles],
                key="roles"
            )
        except Exception as e:
            return response_error(f"Failed to get user roles: {str(e)}", HttpCode.internal_server_error)


    # =============== ASSIGN ROLES TO USER ===============
    @staticmethod
    def assign_roles_to_user(user_id: int, role_ids: list[int]):
        try:
            if not isinstance(role_ids, list):
                return response_error("role_ids must be a list", HttpCode.bad_request)

            UserRole.query.filter_by(user_id=user_id).delete()
            assigned_roles = []

            if role_ids:
                roles = Role.query.filter(Role.id.in_(role_ids)).all()
                valid_role_ids = {r.id for r in roles}

                for role_id in role_ids:
                    if role_id in valid_role_ids:
                        user_role = UserRole(user_id=user_id, role_id=role_id)
                        db.session.add(user_role)
                        assigned_roles.append(
                            next(r.to_dict() for r in roles if r.id == role_id)
                        )

            db.session.commit()

            return response_success(
                assigned_roles,
                key="assigned_roles",
                message="Roles synchronized successfully"
            )
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to assign roles: {str(e)}", HttpCode.internal_server_error)
