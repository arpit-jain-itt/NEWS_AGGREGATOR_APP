def format_response(data=None, success=True, message="", status_code=200):
    return {
        "success": success,
        "data": data,
        "message": message,
    }, status_code
