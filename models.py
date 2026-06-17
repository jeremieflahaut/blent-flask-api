from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Float

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
        }

    def __repr__(self):
        return (
            f"<Product("
            f"id='{self.id}', "
            f"name='{self.name}', "
            f"description='{self.description}', "
            f"price='{self.price}', "
            f"stock='{self.stock}')>"
        )
