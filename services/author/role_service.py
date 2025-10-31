# role_service.py (ĐÃ SỬA)

from database import db
from models.role import Role
from models.user_role import UserRole
from helper.normalization_response import response_error, response_success
from type.http_constants import HttpCode


class RoleService:

    @staticmethod
    def list_roles(list_perm: bool = False):
        """
        Lấy danh sách tất cả các roles.
        Nếu list_perm=True thì trả kèm danh sách permissions của từng role.
        """
        try:
            roles = Role.query.all()
            if not roles:
                # ===================================
                # == BẮT ĐẦU SỬA (1) ==
                # ===================================
                # Bọc list rỗng trong {"roles": []} để khớp RolesResponse type
                return response_success(
                    {"roles": []},
                    message="No roles found",
                    code=HttpCode.success
                )
                # ===================================
                # == KẾT THÚC SỬA (1) ==
                # ===================================

            # Dùng include_permissions theo flag list_perm
            data = [r.to_dict(include_permissions=list_perm) for r in roles]
            
            # ===================================
            # == BẮT ĐẦU SỬA (2) ==
            # ===================================
            # Bọc data (list) trong {"roles": data} để khớp RolesResponse type
            return response_success(
                {"roles": data},
                message="List roles successfully",
                code=HttpCode.success
            )
            # ===================================
            # == KẾT THÚC SỬA (2) ==
            # ===================================
        except Exception as e:
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
        SỬA LẠI: Đồng bộ (SET) roles cho 1 user.
        Xóa tất cả role cũ và thêm tất cả role mới trong list.
        """
        try:
            # SỬA 1: Cho phép role_ids là list (kể cả list rỗng [])
            if not isinstance(role_ids, list):
                return response_error("role_ids must be a list", HttpCode.bad_request)

            # SỬA 2: Xóa tất cả các UserRole hiện tại của user này.
            # Đây là bước quan trọng nhất để "đồng bộ".
            UserRole.query.filter_by(user_id=user_id).delete()

            assigned_roles = []
            
            # SỬA 3: Chỉ chạy vòng lặp nếu list có ID (không phải list rỗng)
            if role_ids: 
                # Kiểm tra các role_ids gửi lên có tồn tại không
                roles = Role.query.filter(Role.id.in_(role_ids)).all()
                
                # Lấy danh sách ID hợp lệ
                valid_role_ids = {r.id for r in roles}
                
                # Thêm các vai trò hợp lệ
                for role_id in role_ids:
                    if role_id in valid_role_ids:
                        user_role = UserRole(user_id=user_id, role_id=role_id)
                        db.session.add(user_role)
                        # (Thêm vào list để trả về)
                        assigned_roles.append(
                            next(r.to_dict() for r in roles if r.id == role_id)
                        )

            # SỬA 4: Commit transaction sau khi đã xóa và thêm
            db.session.commit()

            return response_success(
                assigned_roles, 
                key="assigned_roles", 
                message="Roles synchronized successfully"
            )
            
        except Exception as e:
            db.session.rollback()
            return response_error(f"Failed to assign roles: {str(e)}", HttpCode.internal_server_error)