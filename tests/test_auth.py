import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db


def test_register_ok(client):
    data = {
        "email": "test@example.net",
        "mot_de_passe": "!test123",
        "nom": "John Doe",
    }

    response = client.post("/api/auth/register", json=data)

    assert response.status_code == 201

    user = db.session.execute(
        db.select(User).where(User.email == data["email"])
    ).scalar()

    assert user is not None
    assert user.email == data["email"]
    assert user.password_hash != data["mot_de_passe"]
    assert check_password_hash(user.password_hash, data["mot_de_passe"])

    json = response.json
    assert json["email"] == data["email"]
    assert json.get("mot_de_passe") is None
    assert json["nom"] == data["nom"]


def test_register_duplicate_email(client):
    db.session.add(
        User(
            email="test@example.net",
            password_hash="test",
            role="client",
            name="John Doe",
        )
    )

    db.session.commit()

    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.net",
            "mot_de_passe": "!test123",
            "nom": "John Doe",
        },
    )
    assert response.status_code == 409

    json = response.json
    assert json["error"] == "Email déjà utilisé"


def test_register_missing_errors(client):
    response = client.post(
        "/api/auth/register",
        json={
            "mot_de_passe": "!test123",
            "nom": "John Doe",
        },
    )
    assert response.status_code == 422

    json = response.json
    assert json["error"] == "Données invalides"
    assert "email" in json["details"]


def test_register_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "email invalide",
            "mot_de_passe": "!test123",
            "nom": "John Doe",
        },
    )
    assert response.status_code == 422
    assert response.json["error"] == "Données invalides"
    assert "email" in response.json["details"]


def test_register_password_errors(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.net",
            "mot_de_passe": "test",
            "nom": "John Doe",
        },
    )
    assert response.status_code == 422

    json = response.json
    assert json["error"] == "Données invalides"
    assert "mot_de_passe" in json["details"]

    mdp_errors = response.json["details"]["mot_de_passe"]
    assert "8 caractères minimum" in mdp_errors
    assert "Doit contenir au moins un chiffre" in mdp_errors
    assert "Doit contenir au moins un caractère spécial" in mdp_errors


def test_register_unknown_field(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.net",
            "mot_de_passe": "!test123",
            "nom": "John Doe",
            "role": "admin",
        },
    )
    assert response.status_code == 422
    assert "role" in response.json["details"]


def test_login_ok(client):

    hash = generate_password_hash("test")

    user = User(
        email="test@example.net",
        password_hash=hash,
        role="client",
        name="John Doe",
    )

    db.session.add(user)

    db.session.commit()

    response = client.post(
        "/api/auth/login", json={"email": "test@example.net", "mot_de_passe": "test"}
    )

    assert response.status_code == 200

    json = response.json

    assert "token" in json

    token = jwt.decode(
        json["token"], current_app.config["JWT_SECRET"], algorithms="HS256"
    )

    assert "sub" in token
    assert token["sub"] == str(user.id)


def test_login_wrong_password_and_unknown_email_same_response(client):
    user = User(
        email="test@example.net",
        password_hash=generate_password_hash("!test123"),
        role="client",
        name="John Doe",
    )
    db.session.add(user)
    db.session.commit()

    wrong_password = client.post(
        "/api/auth/login",
        json={"email": "test@example.net", "mot_de_passe": "mauvais!9"},
    )
    unknown_email = client.post(
        "/api/auth/login",
        json={"email": "inconnu@example.net", "mot_de_passe": "!test123"},
    )

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.status_code == unknown_email.status_code
    assert wrong_password.json == unknown_email.json


def test_login_ok_case_insensitive_email(client):

    hash = generate_password_hash("!test123")

    user = User(
        email="test@example.net",
        password_hash=hash,
        role="client",
        name="John Doe",
    )

    db.session.add(user)

    db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": "TEST@example.net", "mot_de_passe": "!test123"},
    )

    assert response.status_code == 200
    assert "token" in response.json


def test_login_missing_fields(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.net"},
    )

    assert response.status_code == 422

    json = response.json
    assert json["error"] == "Données invalides"
    assert "mot_de_passe" in json["details"]


def test_login_invalid_email(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "email invalide", "mot_de_passe": "!test123"},
    )

    assert response.status_code == 422
    assert response.json["error"] == "Données invalides"
