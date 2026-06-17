from flask import Flask
from models import db, Product
from functools import wraps

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def error_response(message: str, code: int):
    return {"error": message}, code


def try_except(func):
    """
    Produit automatiquement une erreur 500 si une exception est levée
    """

    @wraps(func)
    def wrapper(**kwargs):
        try:
            return func(**kwargs)
        except Exception as e:
            return error_response(str(e), 500)

    return wrapper


@app.route("/api/produits", methods=["GET"])
@try_except
def products_index():
    products_db = Product.query.all()

    return [p.to_dict() for p in products_db]


@app.route("/api/produits/<int:id>", methods=["GET"])
@try_except
def product_show(id: int):
    product = Product.query.get(id)

    if product is None:
        return error_response("Product not found", 404)

    return product.to_dict()
