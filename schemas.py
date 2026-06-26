from marshmallow import Schema, fields
from marshmallow.validate import Length, Regexp


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
