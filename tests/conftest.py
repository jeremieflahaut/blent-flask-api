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
                nom="MSI Pro 16 Flex",
                description="PC portable tactile 15.6 pouces",
                categorie="Ordinateurs portables",
                prix=499.0,
                quantite_stock=20,
            ),
            Product(
                nom="Asus TUF Gaming F15",
                description="PC portable gamer 15.6 pouces",
                categorie="Ordinateurs portables",
                prix=899.0,
                quantite_stock=15,
            ),
            Product(
                nom="Logitech G Pro Clavier",
                description="Clavier mécanique pour gamer",
                categorie="Périphériques",
                prix=129.0,
                quantite_stock=30,
            ),
            Product(
                nom="UGreen Souris sans fil",
                description="Souris ergonomique",
                categorie="Périphériques",
                prix=49.99,
                quantite_stock=50,
            ),
        ]

        db.session.add_all(products)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
