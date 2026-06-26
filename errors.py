from marshmallow import ValidationError


def error_response(message: str, code: int, details=None):
    body = {"error": message}
    if details is not None:
        body["details"] = details
    return body, code


def internal_server_error(e):
    return error_response("Erreur interne du serveur", 500)


def validation_error(err):
    return error_response("Données invalides", 422, details=err.messages)


def register_error_handlers(app):
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(ValidationError, validation_error)
