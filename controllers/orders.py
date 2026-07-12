from errors import ApiError
from flask import Blueprint, request, g
from helpers import require_authentication, require_client
from models import Product, Order, OrderLine, db
from schemas import OrderSchema
from constants import STATUT_EN_ATTENTE

orders = Blueprint("orders", __name__, url_prefix="/api/commandes")


def get_order(order_id: int):
    order = db.session.get(Order, order_id)
    if order is None:
        raise ApiError("Commande introuvable", 404)

    user = g.current_user

    if user.role != "admin" and order.user_id != user.id:
        raise ApiError("Accès refusé", 403)

    return order


@orders.route("", methods=["GET"])
@require_authentication
def index():
    user = g.current_user

    query = db.select(Order).order_by(Order.order_date.desc())

    if user.role == "client":
        query = query.where(Order.user_id == user.id)

    items = []

    for item in db.session.scalars(query):
        items.append(item.to_dict())

    return items


@orders.route("/<int:order_id>", methods=["GET"])
@require_authentication
def show(order_id: int):
    order = get_order(order_id)

    return order.to_dict()


@orders.route("/<int:order_id>/lignes", methods=["GET"])
@require_authentication
def show_lines(order_id: int):
    order = get_order(order_id)

    items = []

    for item in order.order_lines:
        items.append(item.to_dict())

    return items


@orders.route("", methods=["POST"])
@require_authentication
@require_client
def store():
    order_schema = OrderSchema()
    data = order_schema.load(request.json)

    order = Order(
        user_id=g.current_user.id,
        delivery_address=data["adresse_livraison"],
        status=STATUT_EN_ATTENTE,
    )

    for item in data["produits"]:
        product = db.session.get(Product, item["produit_id"])

        if product is None:
            raise ApiError("Produit introuvable", 422)

        if item["quantite"] > product.stock_quantity:
            raise ApiError(f"Stock insuffisant pour {product.name}", 422)

        order.order_lines.append(
            OrderLine(
                product=product,
                quantity=item["quantite"],
                unit_price_cents=product.price_cents,
            )
        )

    db.session.add(order)
    db.session.commit()

    return order.to_dict(lines=True), 201
