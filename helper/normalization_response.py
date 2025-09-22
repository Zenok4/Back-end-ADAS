def response_success(data: dict = "", key: str = "data", message = "", code: int = 200):
    response = {
        "success": True,
        "message": message,
        "code": code
    }
    if data:
        response[key] = data
    return response

def response_error(message: str, code: int = 400):
    return {
        "success": False,
        "error": {
            "message": message,
            "code": code
        }
    }
