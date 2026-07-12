import jwt
import pytest
from flask import g
from helpers import require_authentication, require_admin
from models import db, Category, User
from app import create_app
from models import Product, Order
from constants import STATUT_EN_ATTENTE
from datetime import datetime, timedelta, timezone


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET": "9VbNEIFPM9itIDGqjAS6PXas4oDmhqwe",
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()

        @app.get("/test/require-authentication")
        @require_authentication
        def _protected():
            return {"id": g.current_user.id, "role": g.current_user.role}

        @app.get("/test/require-admin")
        @require_authentication
        @require_admin
        def _admin_only():
            return {"ok": True}

        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_token(app):
    def _make(user, **overrides):
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "sub": str(user.id),
        }
        payload.update(overrides)
        return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")

    return _make


@pytest.fixture
def client_user(app):
    user = User(
        email="client@example.net",
        password_hash="password",
        role="client",
        name="CLient",
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app):
    user = User(
        email="admin@example.net", password_hash="password", role="admin", name="Admin"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def make_user(app):
    def _make(**overrides):
        data = {
            "email": "user@example.net",
            "password_hash": "password",
            "role": "client",
            "name": "Utilisateur",
        }
        data.update(overrides)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def categories(app):
    cats = {
        "laptops": Category(name="Ordinateurs portables"),
        "peripherals": Category(name="Périphériques"),
    }
    db.session.add_all(cats.values())
    db.session.commit()
    return cats


@pytest.fixture
def make_product_payload(categories):
    def _make(**overrides):
        data = {
            "nom": "Dell XPS 13",
            "description": "Ultrabook 13 pouces",
            "categorie_id": categories["laptops"].id,
            "prix": 999.90,
            "quantite_stock": 10,
        }
        data.update(overrides)
        return data

    return _make


@pytest.fixture
def products(categories):
    products = [
        Product(
            name="MSI Pro 16 Flex",
            description="PC portable tactile 15.6 pouces",
            category=categories["laptops"],
            price_cents=4990,
            stock_quantity=20,
        ),
        Product(
            name="Asus TUF Gaming F15",
            description="PC portable gamer 15.6 pouces",
            category=categories["laptops"],
            price_cents=8990,
            stock_quantity=15,
        ),
        Product(
            name="Logitech G Pro Clavier",
            description="Clavier mécanique pour gamer",
            category=categories["peripherals"],
            price_cents=1290,
            stock_quantity=30,
        ),
        Product(
            name="UGreen Souris sans fil",
            description="Souris ergonomique",
            category=categories["peripherals"],
            price_cents=4999,
            stock_quantity=50,
        ),
    ]

    db.session.add_all(products)
    db.session.commit()
    return products


@pytest.fixture
def make_order_payload(products):
    def _make(**overrides):
        data = {
            "adresse_livraison": "12 rue de la Paix",
            "produits": [
                {"produit_id": products[0].id, "quantite": 2},
                {"produit_id": products[2].id, "quantite": 1},
            ],
        }
        data.update(overrides)
        return data

    return _make


@pytest.fixture
def make_order(app):
    def _make(user):
        order = Order(
            user_id=user.id,
            delivery_address="12 rue de la Paix",
            status=STATUT_EN_ATTENTE,
        )
        db.session.add(order)
        db.session.commit()
        return order

    return _make
