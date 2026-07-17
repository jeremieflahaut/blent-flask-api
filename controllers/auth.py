import jwt
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from errors import ApiError
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import RegisterSchema, LoginSchema

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route("/register", methods=["POST"])
def register():

    register_schema = RegisterSchema()
    data = register_schema.load(request.json)

    user = User(
        email=data["email"].lower(),
        password_hash=generate_password_hash(data["mot_de_passe"]),
        role="client",
        name=data["nom"],
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("Email déjà utilisé", 409)

    return user.to_dict(), 201


@auth.route("/login", methods=["POST"])
def login():
    login_schema = LoginSchema()
    credentials = login_schema.load(request.json)

    user = db.session.execute(
        db.select(User).where(User.email == credentials["email"].lower())
    ).scalar()

    if user is not None and check_password_hash(
        user.password_hash, credentials["mot_de_passe"]
    ):
        token = jwt.encode(
            {
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "sub": str(user.id),
            },
            current_app.config["JWT_SECRET"],
            algorithm="HS256",
        )

        return jsonify({"token": token}), 200

    raise ApiError("Email ou mot de passe invalide", 401)
