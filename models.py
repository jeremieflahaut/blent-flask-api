from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Float, DateTime

db = SQLAlchemy()


class Product(db.Model):
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    description = Column(Text)
    categorie = Column(String(50), nullable=False)
    prix = Column(Float, nullable=False)
    quantite_stock = Column(Integer, default=0)
    date_creation = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "description": self.description,
            "categorie": self.categorie,
            "prix": self.prix,
            "quantite_stock": self.quantite_stock,
            "date_creation": (
                self.date_creation.isoformat() if self.date_creation else None
            ),
        }

    def __repr__(self):
        return (
            f"<Product("
            f"id='{self.id}', "
            f"nom='{self.nom}', "
            f"categorie='{self.categorie}', "
            f"prix='{self.prix}', "
            f"quantite_stock='{self.quantite_stock}')>"
        )
