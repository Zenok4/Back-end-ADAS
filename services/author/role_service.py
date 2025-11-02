from database import db
from models.role import Role
from models.user_role import UserRole
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode


class RoleService:

    @staticmethod
    #Thêm phân trang
    #Thêm tổng số roles
    #thêm filter theo tên, mô tả, trạng thái,...
    def list_roles(
        page = 1,
        limit = 20,
        name = None,
        description = None,
        is_active = None,
        list_perm: bool = False
        ):
        """
        Lấy danh sách tất cả các roles.
        Nếu list_perm=True thì trả kèm danh sách permissions của từng role.
        """
        try:
            query = Role.query
            if name:
                query = query.filter(Role.name.ilike(f"%{name}%"))
            if description:
                query = query.filter(Role.description.ilike(f"%{description}%"))
            if is_active is not None:
                if isinstance(is_active, str):
                    is_active_bool = is_active.lower() == 'true'
                else:
                    is_active_bool = bool(is_active)
                query = query.filter(Role.is_active == is_active_bool)

            total = query.count()
            roles = (
                query.order_by(Role.id.desc())
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )
            data = [r.to_dict(include_permissions=list_perm) for r in roles]
            payload = {
                "roles": data,
                "page": page,
                "limit": limit,
                "total": total,
            }
            return response_success(
                payload,
                message="List roles successfully",
                code=HttpCode.success
            )

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Database error: {str(e)}", HttpCode.internal_server_error)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to list roles: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def get_role_by_id(role_id: int, include_permissions: bool = False):
        """
        Lấy thông tin chi tiết 1 role theo id.
        Nếu include_permissions=True => trả kèm danh sách permission.
        """
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

    @staticmethod
    def get_role_by_name(name: str, include_permissions: bool = False):
        """
        Lấy thông tin chi tiết 1 role theo tên.
        Nếu include_permissions=True => trả kèm danh sách permission.
        """
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
    def get_user_roles(user_id: int, include_permissions: bool = False):
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
            if not roles:
                return response_success([], key="roles", message="User has no roles")
            return response_success([r.to_dict(include_permissions=include_permissions) for r in roles], key="roles")
        except Exception as e:
            return response_error(f"Failed to get user roles: {str(e)}", HttpCode.internal_server_error)

    @staticmethod
    def assign_roles_to_user(user_id: int, role_ids: list[int]):
        """
        Gán nhiều roles cho 1 user.
        """
        try:
            if not role_ids or not isinstance(role_ids, list):
                return response_error("role_ids must be a non-empty list", HttpCode.bad_request)

            # Kiểm tra roles tồn tại
            roles = Role.query.filter(Role.id.in_(role_ids)).all()
            if not roles:
                return response_error("No valid roles found", HttpCode.not_found)

            assigned_roles = []
            for role in roles:
                # Kiểm tra xem user đã có role này chưa
                existing = UserRole.query.filter_by(user_id=user_id, role_id=role.id).first()
                if not existing:
                    user_role = UserRole(user_id=user_id, role_id=role.id)
                    db.session.add(user_role)
                    assigned_roles.append(role.to_dict())

            db.session.commit()

            if not assigned_roles:
                return response_success([], key="assigned_roles", message="User already has all these roles")

            return response_success(assigned_roles, key="assigned_roles", message="Roles assigned successfully")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to assign roles: {str(e)}", HttpCode.internal_server_error)
