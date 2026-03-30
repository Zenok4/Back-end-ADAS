from database import db
from middlewares.permission_required import clear_permissions_cache
from models.role import Role
from models.user_role import UserRole
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode
from sqlalchemy import exc
from services.audit_log_service import AuditLogService


class RoleService:

    # =============== LIST ALL ROLES ===============
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
    def create_role(name: str, description: str = None, is_active: bool = True, level: int = 1, current_user_level: int = 0):
        try:
            # === LOGIC BẢO MẬT ===
            # Level của role sắp tạo phải nhỏ hơn level của người tạo
            if level >= current_user_level:
                return response_error(
                    f"Cannot create role with level ({level}) higher than or equal to your own level ({current_user_level})", 
                    HttpCode.forbidden
                )
            # =================================

            role = Role(name=name, description=description, is_active=is_active, level=level)
            db.session.add(role)
            db.session.commit()
            clear_permissions_cache()
            AuditLogService.log_action(user_id=None, action="CREATE", object_type="ROLE", object_id=role.id)
            return response_success(role.to_dict(), key="role", message="Role created", code=HttpCode.created)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Create role failed: {str(e)}", HttpCode.internal_server_error)


    # =============== UPDATE ROLE ===============
    @staticmethod
    def update_role(role_id: int,current_user_level: int = 0, **kwargs):

        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)

            # === LOGIC BẢO MẬT ===
            # 1. Không cho phép sửa role có level cao hơn hoặc bằng mình
            if role.level > current_user_level:
                return response_error(
                    f"Cannot update role ({role.name}) because their level ({role.level}) is equal to or higher than your own ({current_user_level})", 
                    HttpCode.forbidden
                )
            
            # 2. Không cho phép gán level mới cao hơn hoặc bằng level của mình
            if 'level' in kwargs and kwargs['level'] >= current_user_level:
                 return response_error(
                    f"Cannot assign new level ({kwargs['level']}) higher than or equal to your own level ({current_user_level})", 
                    HttpCode.forbidden
                )
            # =================================

            for key, value in kwargs.items():
                if hasattr(role, key):
                    setattr(role, key, value) 

            db.session.commit()
            clear_permissions_cache()
            AuditLogService.log_action(user_id=None, action="UPDATE", object_type="ROLE", object_id=role.id)
            return response_success(role.to_dict(), key="role", message="Role updated")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Update failed: {str(e)}", HttpCode.internal_server_error)


    # =============== DELETE ROLE ===============
    @staticmethod
    def delete_role(role_id: int, current_user_level: int = 0):
        try:
            role = Role.query.get(role_id)
            if not role:
                return response_error("Role not found", HttpCode.not_found)

            # === LOGIC BẢO MẬT  ===
            # Không cho phép xóa role có level cao hơn hoặc bằng mình
            if role.level >= current_user_level:
                 return response_error(
                    f"Cannot delete role ({role.name}) because their level ({role.level}) is equal to or higher than your own level ({current_user_level})", 
                    HttpCode.forbidden
                )
            # =================================

            db.session.delete(role)
            db.session.commit()
            clear_permissions_cache()
            AuditLogService.log_action(user_id=None, action="DELETE", object_type="ROLE", object_id=role_id)
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
            clear_permissions_cache()
            AuditLogService.log_action(user_id=user_id, action="ASSIGN_ROLES", object_type="USER", object_id=user_id, new_values={"roles": role_ids})
            return response_success(
                assigned_roles,
                key="assigned_roles",
                message="Roles synchronized successfully"
            )
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to assign roles: {str(e)}", HttpCode.internal_server_error)
