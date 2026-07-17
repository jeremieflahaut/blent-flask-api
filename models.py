from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    event,
    Engine,
)

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Product(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_id = Column(ForeignKey("category.id", ondelete="RESTRICT"), nullable=False)
    price_cents = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, default=0)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    category = db.relationship("Category", backref="products")

    @property
    def price_euros(self):
        return self.price_cents / 100

    @price_euros.setter
    def price_euros(self, value):
        self.price_cents = round(value * 100)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.name,
            "description": self.description,
            "categorie": {"id": self.category_id, "nom": self.category.name},
            "prix": self.price_euros,
            "quantite_stock": self.stock_quantity,
            "date_creation": self.created_at.isoformat(),
        }

    def __repr__(self):
        return (
            f"<Product("
            f"id='{self.id}', "
            f"name='{self.name}', "
            f"category_id='{self.category_id}', "
            f"price_cents='{self.price_cents}', "
            f"stock_quantity='{self.stock_quantity}', "
            f"created_at='{self.created_at}')>"
        )


class Category(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.name,
            "date_creation": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Category(id='{self.id}', " f"name='{self.name}')>"


class User(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "nom": self.name,
            "role": self.role,
            "date_creation": self.created_at.isoformat(),
        }

    def __repr__(self):
        return (
            f"<User("
            f"id='{self.id}', "
            f"email='{self.email}', "
            f"nom='{self.name}', "
            f"role='{self.role}', "
            f"created_at='{self.created_at}')>"
        )


class Order(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.id", ondelete="RESTRICT"), nullable=False)
    order_date = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    delivery_address = Column(Text, nullable=False)
    status = Column(String(100), nullable=False)

    user = db.relationship("User", backref="orders")

    def to_dict(self, lines=False):
        data = {
            "id": self.id,
            "utilisateur": {"id": self.user_id, "nom": self.user.name},
            "date_commande": self.order_date.isoformat(),
            "adresse_livraison": self.delivery_address,
            "statut": self.status,
        }

        if lines:
            data["lignes"] = [ligne.to_dict() for ligne in self.order_lines]
        return data

    def __repr__(self):
        return (
            f"<Order(id='{self.id}', "
            f"user_id='{self.user_id}', "
            f"order_date='{self.order_date}', "
            f"status='{self.status}')>"
        )


class OrderLine(db.Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)

    product = db.relationship("Product", backref="order_lines")
    order = db.relationship("Order", backref="order_lines")

    @property
    def price_euros(self):
        return self.unit_price_cents / 100

    @price_euros.setter
    def price_euros(self, value):
        self.unit_price_cents = round(value * 100)

    def to_dict(self):
        return {
            "id": self.id,
            "commande_id": self.order_id,
            "produit": {"id": self.product_id, "nom": self.product.name},
            "quantite": self.quantity,
            "prix_unitaire": self.price_euros,
        }

    def __repr__(self):
        return (
            f"<OrderLine(id='{self.id}', "
            f"order_id='{self.order_id}', "
            f"product_id='{self.product_id}', "
            f"quantity='{self.quantity}', "
            f"unit_price_cents='{self.unit_price_cents}')>"
        )
