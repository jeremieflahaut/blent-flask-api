from marshmallow import Schema, fields
from marshmallow.validate import Length, Regexp, Range, OneOf

from constants import STATUTS


class RegisterSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "email requis",
            "invalid": "email n'est pas une adresse valide",
        },
    )
    mot_de_passe = fields.Str(
        required=True,
        error_messages={
            "required": "mot de passe requis",
        },
        validate=[
            Length(min=8, error="8 caractères minimum"),
            Regexp(r".*\d", error="Doit contenir au moins un chiffre"),
            Regexp(r".*[^\w\s]", error="Doit contenir au moins un caractère spécial"),
        ],
    )
    nom = fields.Str(
        required=True,
        error_messages={
            "required": "nom requis",
        },
    )


class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "email requis",
            "invalid": "email n'est pas une adresse valide",
        },
    )
    mot_de_passe = fields.Str(
        required=True,
        error_messages={
            "required": "mot de passe requis",
        },
    )


class ProductSchema(Schema):
    nom = fields.Str(
        required=True,
        error_messages={
            "required": "nom requis",
        },
    )
    description = fields.Str(
        required=True,
        error_messages={
            "required": "description requis",
        },
    )
    categorie_id = fields.Int(
        required=True,
        error_messages={"required": "categorie_id requis"},
    )
    prix = fields.Decimal(
        places=2,
        required=True,
        validate=Range(min=0, min_inclusive=False, error="Le prix doit être positif"),
        error_messages={
            "required": "prix requis",
        },
    )
    quantite_stock = fields.Int(
        required=True,
        validate=Range(min=0, error="Le stock ne peut pas être négatif"),
        error_messages={
            "required": "stock_quantity requis",
        },
    )


class OrderProductSchema(Schema):
    produit_id = fields.Int(
        required=True,
        error_messages={
            "required": "produit_id requis",
        },
    )
    quantite = fields.Int(
        required=True,
        validate=Range(min=1, error="La quantité doit être de 1 ou plus"),
        error_messages={
            "required": "quantite requis",
        },
    )


class OrderSchema(Schema):
    produits = fields.List(
        fields.Nested(OrderProductSchema),
        required=True,
        validate=Length(min=1, error="La commande doit contenir au moins un produit"),
        error_messages={
            "required": "produits requis",
        },
    )
    adresse_livraison = fields.Str(
        required=True,
        error_messages={
            "required": "adresse_livraison requis",
        },
    )


class OrderStatusSchema(Schema):
    statut = fields.Str(
        required=True,
        validate=OneOf(STATUTS, error="statut invalide"),
        error_messages={
            "required": "statut requis",
        },
    )
