from enum import IntEnum, Enum

class HttpCode(IntEnum):
    # 2xx Success
    success = 200
    created = 201
    accepted = 202
    no_content = 204

    # 3xx Redirection
    moved_permanently = 301
    found = 302
    not_modified = 304

    # 4xx Client Error
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    not_found = 404
    not_acceptable = 406
    conflict = 409

    # 5xx Server Error
    internal_server_error = 500
    not_implemented = 501
    bad_gateway = 502
    service_unavailable = 503

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"