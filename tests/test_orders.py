from constants import STATUT_EN_ATTENTE
from models import db, Order, Product


def test_orders_store_requires_authentication(client, make_order_payload):
    response = client.post("/api/commandes", json=make_order_payload())
    assert response.status_code == 401


def test_orders_store_ok_for_client(
    client, client_user, make_token, make_order_payload
):
    token = make_token(client_user)
    data = make_order_payload()
    response = client.post(
        "/api/commandes",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    json = response.json
    assert json["id"] is not None
    assert json["utilisateur"]["id"] == client_user.id
    assert json["utilisateur"]["nom"] == client_user.name
    assert json["adresse_livraison"] == data["adresse_livraison"]
    assert json["statut"] == STATUT_EN_ATTENTE
    assert len(json["lignes"]) == 2


def test_orders_store_forbidden_for_admin(
    client, admin_user, make_token, make_order_payload
):
    token = make_token(admin_user)
    response = client.post(
        "/api/commandes",
        json=make_order_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_orders_store_freezes_unit_price(
    client, client_user, make_token, make_order_payload, products
):
    token = make_token(client_user)
    response = client.post(
        "/api/commandes",
        json=make_order_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    order = db.session.get(Order, response.json["id"])
    assert len(order.order_lines) == 2
    assert order.order_lines[0].unit_price_cents == products[0].price_cents


def test_orders_store_does_not_decrement_stock(
    client, client_user, make_token, make_order_payload, products
):
    token = make_token(client_user)
    response = client.post(
        "/api/commandes",
        json=make_order_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert db.session.get(Product, products[0].id).stock_quantity == 20
    assert db.session.get(Product, products[2].id).stock_quantity == 30


def test_orders_store_unknown_product(
    client, client_user, make_token, make_order_payload
):
    token = make_token(client_user)
    data = make_order_payload(produits=[{"produit_id": 9999, "quantite": 1}])
    response = client.post(
        "/api/commandes",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json["error"] == "Produit introuvable"


def test_orders_store_insufficient_stock(
    client, client_user, make_token, make_order_payload, products
):
    token = make_token(client_user)
    data = make_order_payload(
        produits=[{"produit_id": products[0].id, "quantite": 9999}]
    )
    response = client.post(
        "/api/commandes",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "Stock insuffisant" in response.json["error"]


def test_orders_store_empty_cart(client, client_user, make_token, make_order_payload):
    token = make_token(client_user)
    data = make_order_payload(produits=[])
    response = client.post(
        "/api/commandes",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "produits" in response.json["details"]


def test_orders_store_missing_produits(
    client, client_user, make_token, make_order_payload
):
    token = make_token(client_user)
    data = make_order_payload()
    del data["produits"]
    response = client.post(
        "/api/commandes",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "produits" in response.json["details"]


def test_orders_store_missing_address(
    client, client_user, make_token, make_order_payload
):
    token = make_token(client_user)
    data = make_order_payload()
    del data["adresse_livraison"]
    response = client.post(
        "/api/commandes",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "adresse_livraison" in response.json["details"]
