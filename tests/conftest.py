import pytest
from models import db, Category
from app import create_app
from models import Product


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

        cat_laptops = Category(name="Ordinateurs portables")
        cat_peripherals = Category(name="Périphériques")
        db.session.add_all([cat_laptops, cat_peripherals])

        products = [
            Product(
                name="MSI Pro 16 Flex",
                description="PC portable tactile 15.6 pouces",
                category=cat_laptops,
                price_cents=4990,
                stock_quantity=20,
            ),
            Product(
                name="Asus TUF Gaming F15",
                description="PC portable gamer 15.6 pouces",
                category=cat_laptops,
                price_cents=8990,
                stock_quantity=15,
            ),
            Product(
                name="Logitech G Pro Clavier",
                description="Clavier mécanique pour gamer",
                category=cat_peripherals,
                price_cents=1290,
                stock_quantity=30,
            ),
            Product(
                name="UGreen Souris sans fil",
                description="Souris ergonomique",
                category=cat_peripherals,
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
