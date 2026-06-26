from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from errors import error_response
from models import User, db
from werkzeug.security import generate_password_hash
from schemas import RegisterSchema

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route("/register", methods=["POST"])
def register():

    register_schema = RegisterSchema()
    data = register_schema.load(request.json)

    user = User(
        email=data["email"],
        password_hash=generate_password_hash(data["mot_de_passe"]),
        role="client",
        name=data["nom"],
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response("Email déjà utilisé", 409)

    return user.to_dict(), 201
