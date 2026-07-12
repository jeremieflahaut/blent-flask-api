from errors import error_response
from flask import Blueprint, request, g
from helpers import require_authentication, require_client
from models import Product, Order, OrderLine, db
from schemas import OrderSchema
from constants import STATUT_EN_ATTENTE

orders = Blueprint("orders", __name__, url_prefix="/api/commandes")


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
            return error_response("Produit introuvable", 422)

        if item["quantite"] > product.stock_quantity:
            return error_response(f"Stock insuffisant pour {product.name}", 422)

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
