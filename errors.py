from marshmallow import ValidationError


class ApiError(Exception):
    """Erreur métier convertie en réponse HTTP par le handler global `api_error`.

    On la lève (au lieu de retourner `error_response`) pour qu'elle remonte
    depuis n'importe quelle couche — helper, contrôleur — sans que l'appelant
    ait à la détecter ni à la relayer.
    """

    def __init__(self, message, code):
        super().__init__(message)
        self.message = message
        self.code = code


def error_response(message: str, code: int, details=None):
    body = {"error": message}
    if details is not None:
        body["details"] = details
    return body, code


def internal_server_error(e):
    return error_response("Erreur interne du serveur", 500)


def validation_error(err):
    return error_response("Données invalides", 422, details=err.messages)


def api_error(err):
    return error_response(err.message, err.code)


def register_error_handlers(app):
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(ValidationError, validation_error)
    app.register_error_handler(ApiError, api_error)
