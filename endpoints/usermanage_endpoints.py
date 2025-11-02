from flask import Blueprint, request, jsonify
from services.authen.user_service import UserService
from type.http_constants import HttpCode
from helper.normalization_response import response_error

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

# ================== LIST ==================
@user_bp.route("/list", methods=["GET"])
def list_users():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        keyword = request.args.get("keyword", "")
        result = UserService.get_all_users(page, limit, keyword)
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== DETAIL BY ID ==================
@user_bp.route("/id/<int:user_id>", methods=["GET"])
def get_user_detail(user_id):
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"
    result = UserService.get_user_by_id(user_id, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== DETAIL BY USERNAME ==================
@user_bp.route("/username/<string:username>", methods=["GET"])
def get_user_by_username(username):
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"
    result = UserService.get_user_by_username(username, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== FILTER BY ACTIVE STATUS ==================
@user_bp.route("/active/<string:is_active>", methods=["GET"])
def list_users_by_active(is_active):
    data = request.args
    include_roles = data.get("include_roles", "false").lower() == "true"
    is_active_bool = is_active.lower() == "true"
    result = UserService.get_users_by_active(is_active_bool, include_roles=include_roles)
    return jsonify(result), result.get("code", HttpCode.success)


# ================== CREATE ==================
@user_bp.route("/create", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.create_user(data)
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
        return jsonify(result), result.get("code", HttpCode.created)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== UPDATE ==================
@user_bp.route("/update/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.update_user(user_id, data)
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== DELETE ==================
@user_bp.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        result = UserService.delete_user(user_id)
        if not result.get("success", False):
            return jsonify(result), result.get("code", HttpCode.not_found)
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error


# ================== TOGGLE STATUS ==================
@user_bp.route("/status/<int:user_id>", methods=["PATCH"])
def toggle_user_status(user_id):
    data = request.get_json(silent=True) or {}
    try:
        result = UserService.toggle_status(user_id, data)
        if not result.get("success"):
            return jsonify(result), result.get("code", HttpCode.bad_request)
        return jsonify(result), result.get("code", HttpCode.success)
    except Exception as e:
        return jsonify(response_error(
            message=f"Internal server error: {e}",
            code=HttpCode.internal_server_error
        )), HttpCode.internal_server_error
