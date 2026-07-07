from marshmallow import Schema, fields
from marshmallow.validate import Length, Regexp, Range


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
    category_id = fields.Int(
        required=True,
        error_messages={"required": "category_id requis"},
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
