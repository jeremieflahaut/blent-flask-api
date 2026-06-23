def error_response(message: str, code: int):
    return {"error": message}, code


def internal_server_error(e):
    return error_response("Internal Server Error", 500)


def register_error_handlers(app):
    app.register_error_handler(500, internal_server_error)
