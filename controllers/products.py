from flask import Blueprint, request
from errors import error_response
from helpers import require_authentication, require_admin
from models import db, Product, Category
from schemas import ProductSchema
from sqlalchemy import or_

products = Blueprint("products", __name__, url_prefix="/api/produits")


@products.route("", methods=["GET"])
def index():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    search = request.args.get("search", default=None, type=str)

    query = db.select(Product)

    if search is not None:
        for word in search.split():
            query = query.where(
                or_(
                    Product.name.ilike(f"%{word}%"),
                    Product.description.ilike(f"%{word}%"),
                )
            )

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        "items": [p.to_dict() for p in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


@products.route("", methods=["POST"])
@require_authentication
@require_admin
def store():
    product_schema = ProductSchema()
    data = product_schema.load(request.json)

    category = db.session.get(Category, data["categorie_id"])
    if category is None:
        return error_response("Catégorie introuvable", 422)

    product = Product(
        name=data["nom"],
        description=data["description"],
        category_id=category.id,
        price_cents=round(data["prix"] * 100),
        stock_quantity=data["quantite_stock"],
    )

    db.session.add(product)
    db.session.commit()

    return product.to_dict(), 201


@products.route("/<int:product_id>", methods=["GET"])
def show(product_id: int):
    product = db.session.get(Product, product_id)

    if product is None:
        return error_response("Produit introuvable", 404)

    return product.to_dict()


@products.route("/<int:product_id>", methods=["PUT"])
@require_authentication
@require_admin
def update(product_id: int):
    product_schema = ProductSchema()
    data = product_schema.load(request.json)

    product = db.session.get(Product, product_id)
    if product is None:
        return error_response("Produit introuvable", 404)

    category = db.session.get(Category, data["categorie_id"])
    if category is None:
        return error_response("Catégorie introuvable", 422)

    product.name = data["nom"]
    product.description = data["description"]
    product.category_id = category.id
    product.price_cents = round(data["prix"] * 100)
    product.stock_quantity = data["quantite_stock"]
    db.session.commit()
    return product.to_dict(), 200


@products.route("/<int:product_id>", methods=["DELETE"])
@require_authentication
@require_admin
def delete(product_id: int):
    product = db.session.get(Product, product_id)

    if product is None:
        return error_response("Produit introuvable", 404)

    db.session.delete(product)
    db.session.commit()

    return "", 204
