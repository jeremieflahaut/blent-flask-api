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
            "categorie": self.category.name,
            "prix": self.price_euros,
            "quantite_stock": self.stock_quantity,
            "date_creation": self.created_at.isoformat(),
        }

    def __repr__(self):
        return (
            f"<Product("
            f"id='{self.id}', "
            f"name='{self.name}', "
            f"category='{self.category}', "
            f"price_cents='{self.price_cents}', "
            f"stock_quantity='{self.stock_quantity}'"
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
    date_creation = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
