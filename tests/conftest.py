import pytest
from models import db
from app import create_app
from models import Product


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        products = [
            Product(
                name="MSI Pro 16 Flex",
                description="PC portable tactile 15.6 pouces",
                category="Ordinateurs portables",
                price_cents=4990,
                stock_quantity=20,
            ),
            Product(
                name="Asus TUF Gaming F15",
                description="PC portable gamer 15.6 pouces",
                category="Ordinateurs portables",
                price_cents=8990,
                stock_quantity=15,
            ),
            Product(
                name="Logitech G Pro Clavier",
                description="Clavier mécanique pour gamer",
                category="Périphériques",
                price_cents=1290,
                stock_quantity=30,
            ),
            Product(
                name="UGreen Souris sans fil",
                description="Souris ergonomique",
                category="Périphériques",
                price_cents=4999,
                stock_quantity=50,
            ),
        ]

        db.session.add_all(products)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
