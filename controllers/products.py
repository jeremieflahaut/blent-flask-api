from functools import wraps

from flask import Blueprint

from models import Product

products = Blueprint("products", __name__, url_prefix="/api/produits")


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


@products.route("", methods=["GET"])
@try_except
def index():
    products_db = Product.query.all()

    return [p.to_dict() for p in products_db]


@products.route("/<int:product_id>", methods=["GET"])
@try_except
def show(product_id: int):
    product = Product.query.get(product_id)

    if product is None:
        return error_response("Product not found", 404)

    return product.to_dict()
