import functools

import jwt
from flask import current_app, request, g

from errors import error_response
from models import db, User


def decode_token(token):
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms="HS256")
    except Exception:
        return None


def require_authentication(f):
    @functools.wraps(f)
    def wrapper(**kwargs):
        authorisation = request.headers.get("Authorization")
        if authorisation:
            parts = authorisation.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
            else:
                return error_response("Token invalide", 401)
        else:
            token = None

        payload = decode_token(token)
        if not payload:
            return error_response("Email ou mot de passe invalide", 401)

        user = db.session.get(User, int(payload["sub"]))
        if user is None:
            return error_response("Email ou mot de passe invalide", 401)

        g.current_user = user

        return f(**kwargs)

    return wrapper


def require_admin(f):
    @functools.wraps(f)
    def wrapper(**kwargs):
        user = g.get("current_user")
        if user is None:
            return error_response("Email ou mot de passe invalide", 401)

        if user.role != "admin":
            return error_response("Accès refusé", 403)

        return f(**kwargs)

    return wrapper
