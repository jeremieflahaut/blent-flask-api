from werkzeug.security import generate_password_hash

from app import create_app
from models import db, Product, Category, User, Order, OrderLine
from constants import STATUT_EN_ATTENTE, STATUT_ANNULEE

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    cat_laptops = Category(name="Ordinateurs portables")
    cat_peripherals = Category(name="Périphériques")

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

    users = [
        User(
            email="admin@digimarket.fr",
            password_hash=generate_password_hash("admin1234!"),
            role="admin",
            name="Admin DigiMarket",
        ),
        User(
            email="client@digimarket.fr",
            password_hash=generate_password_hash("client1234!"),
            role="client",
            name="Jean Client",
        ),
    ]

    client = users[1]

    commande_en_attente = Order(
        user=client,
        delivery_address="12 rue de la Paix, 75002 Paris",
        status=STATUT_EN_ATTENTE,
    )
    commande_en_attente.order_lines.append(
        OrderLine(
            product=products[0],
            quantity=1,
            unit_price_cents=products[0].price_cents,
        )
    )
    commande_en_attente.order_lines.append(
        OrderLine(
            product=products[2],
            quantity=2,
            unit_price_cents=products[2].price_cents,
        )
    )

    commande_annulee = Order(
        user=client,
        delivery_address="5 avenue Victor Hugo, 69003 Lyon",
        status=STATUT_ANNULEE,
    )
    commande_annulee.order_lines.append(
        OrderLine(
            product=products[3],
            quantity=1,
            unit_price_cents=products[3].price_cents,
        )
    )

    db.session.add_all([cat_laptops, cat_peripherals])
    db.session.add_all(products)
    db.session.add_all(users)
    db.session.add_all([commande_en_attente, commande_annulee])

    db.session.commit()
