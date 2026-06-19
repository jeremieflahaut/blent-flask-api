from app import create_app
from models import db, Product

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    products = [
        Product(
            name="MSI Pro 16 Flex",
            description="PC portable tactile 15.6 pouces",
            price=499.0,
            stock=20,
        ),
        Product(
            name="Asus TUF Gaming F15",
            description="PC portable gamer 15.6 pouces",
            price=899.0,
            stock=15,
        ),
        Product(
            name="Logitech G Pro Clavier",
            description="Clavier mécanique pour gamer",
            price=129.0,
            stock=30,
        ),
        Product(
            name="UGreen Souris sans fil",
            description="Souris ergonomique",
            price=49.99,
            stock=50,
        ),
    ]

    db.session.add_all(products)
    db.session.commit()
