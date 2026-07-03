from flask import Blueprint, request

from errors import error_response
from models import db, Product

products = Blueprint("products", __name__, url_prefix="/api/produits")


@products.route("", methods=["GET"])
def index():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    pagination = db.paginate(
        db.select(Product), page=page, per_page=per_page, error_out=False
    )

    return {
        "items": [p.to_dict() for p in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


@products.route("/<int:product_id>", methods=["GET"])
def show(product_id: int):
    product = db.session.get(Product, product_id)

    if product is None:
        return error_response("Produit introuvable", 404)

    return product.to_dict()
