
from functools import wraps

from flask import jsonify

from helper.normalization_response import response_error
from type.http_constants import HttpCode


def handle_exceptions(fn):
    """
    Decorator chung để bắt ngoại lệ không lường trước,
    trả về response_error chuẩn giống các endpoint auth.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            # TODO: log exception e (ví dụ: logging.exception(e))
            return (
                jsonify(
                    response_error(
                        message="Internal server error",
                        code=HttpCode.internal_server_error
                    )
                ),
                HttpCode.internal_server_error,
            )
    return wrapper