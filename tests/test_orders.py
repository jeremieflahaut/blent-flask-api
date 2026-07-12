from constants import STATUT_EN_ATTENTE
from models import db, Order, OrderLine, Product


def test_orders_index_requires_authentication(client):
    response = client.get("/api/commandes")
    assert response.status_code == 401


def test_orders_index_client_sees_only_own(
    client, client_user, make_user, make_token, make_order
):
    other = make_user(email="other@example.net", name="Autre")

    own_order = make_order(client_user)
    make_order(other)

    token = make_token(client_user)
    response = client.get(
        "/api/commandes",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["id"] == own_order.id
    assert response.json[0]["utilisateur"]["id"] == client_user.id


def test_orders_index_admin_sees_all(
    client, admin_user, client_user, make_token, make_order
):
    make_order(client_user)
    make_order(admin_user)

    token = make_token(admin_user)
    response = client.get(
        "/api/commandes",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json) == 2


def test_orders_show_requires_authentication(client, client_user, make_order):
    order = make_order(client_user)

    response = client.get(f"/api/commandes/{order.id}")
    assert response.status_code == 401


def test_orders_show_owner_can_view(
    client, client_user, make_token, make_order, products
):
    order = make_order(client_user)
    order.order_lines.append(
        OrderLine(
            product=products[0],
            quantity=2,
            unit_price_cents=products[0].price_cents,
        )
    )
    db.session.commit()

    token = make_token(client_user)
    response = client.get(
        f"/api/commandes/{order.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["id"] == order.id
    assert len(response.json["lignes"]) == 1


def test_orders_show_forbidden_for_other_client(
    client, client_user, make_user, make_token, make_order
):
    other = make_user(email="other@example.net", name="Autre")

    order = make_order(other)

    token = make_token(client_user)
    response = client.get(
        f"/api/commandes/{order.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_orders_show_admin_can_view_any(
    client, admin_user, client_user, make_token, make_order
):
    order = make_order(client_user)

    token = make_token(admin_user)
    response = client.get(
        f"/api/commandes/{order.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["id"] == order.id


def test_orders_show_not_found(client, client_user, make_token):
    token = make_token(client_user)
    response = client.get(
        "/api/commandes/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


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
