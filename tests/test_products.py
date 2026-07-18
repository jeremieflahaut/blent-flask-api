from models import db, Product


def test_products_index_empty(client):
    response = client.get("/api/produits")
    assert response.status_code == 200

    json = response.json
    assert len(json["items"]) == 0


def test_products_index_page_out_of_range(client):
    response = client.get("/api/produits?page=2&per_page=2")
    assert response.status_code == 200

    json = response.json

    assert json["page"] == 2
    assert json["per_page"] == 2
    assert json["total"] == 0
    assert json["pages"] == 0
    assert len(json["items"]) == 0


def test_products_index(client, products):
    response = client.get("/api/produits?page=2&per_page=2")
    assert response.status_code == 200

    json = response.json

    assert json["page"] == 2
    assert json["per_page"] == 2
    assert json["total"] == 4
    assert json["pages"] == 2
    assert len(json["items"]) == 2

    for produit in json["items"]:
        assert produit["id"] is not None
        assert produit["nom"] is not None
        assert produit["description"] is not None
        assert produit["categorie"] is not None
        assert produit["prix"] is not None
        assert produit["quantite_stock"] is not None
        assert produit["date_creation"] is not None


def test_products_index_per_page_is_capped(client, products):
    response = client.get("/api/produits?per_page=100000")
    assert response.status_code == 200

    json = response.json

    # max_per_page=25 : la valeur demandée est ramenée au plafond
    assert json["per_page"] == 25


def test_products_show(client, products):
    response = client.get("/api/produits/1")
    assert response.status_code == 200

    produit = response.json

    assert produit["id"] == 1
    assert produit["nom"] == "MSI Pro 16 Flex"
    assert produit["description"] is not None
    assert produit["categorie"]["id"] == 1
    assert produit["categorie"]["nom"] == "Ordinateurs portables"
    assert produit["prix"] == 49.90
    assert produit["quantite_stock"] is not None
    assert produit["date_creation"] is not None


def test_products_show_404(client):
    response = client.get("/api/produits/5")
    assert response.status_code == 404
    assert response.json["error"] == "Produit introuvable"


def test_products_search_by_name(client, products):
    response = client.get("/api/produits?search=asus")
    assert response.status_code == 200

    json = response.json
    assert json["total"] == 1
    assert json["items"][0]["nom"] == "Asus TUF Gaming F15"


def test_products_search_in_description(client, products):
    response = client.get("/api/produits?search=ergonomique")
    assert response.status_code == 200

    json = response.json
    assert json["total"] == 1
    assert json["items"][0]["nom"] == "UGreen Souris sans fil"


def test_products_search_case_insensitive(client, products):
    response = client.get("/api/produits?search=ASUS")
    assert response.status_code == 200
    assert response.json["total"] == 1


def test_products_search_multiple_words_and(client, products):
    response = client.get("/api/produits?search=asus souris")
    assert response.status_code == 200
    assert response.json["total"] == 0


def test_products_search_no_match(client, products):
    response = client.get("/api/produits?search=xyzzy")
    assert response.status_code == 200

    json = response.json
    assert json["total"] == 0
    assert json["items"] == []


def test_products_store_requires_authentication(client, make_product_payload):
    response = client.post("/api/produits", json=make_product_payload())
    assert response.status_code == 401


def test_products_store_forbidden_for_client(
    client, client_user, make_token, make_product_payload
):
    token = make_token(client_user)
    response = client.post(
        "/api/produits",
        json=make_product_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_products_store_ok_for_admin(
    client, categories, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload()
    response = client.post(
        "/api/produits",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    json = response.json
    assert json["id"] is not None
    assert json["nom"] == data["nom"]
    assert json["prix"] == data["prix"]
    assert json["categorie"]["id"] == categories["laptops"].id
    assert json["categorie"]["nom"] == "Ordinateurs portables"

    product = db.session.get(Product, json["id"])
    assert product is not None
    assert product.name == data["nom"]
    assert product.price_cents == 99990
    assert product.category_id == categories["laptops"].id


def test_products_store_unknown_category(
    client, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload(categorie_id=9999)
    response = client.post(
        "/api/produits",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json["error"] == "Catégorie introuvable"


def test_products_store_missing_field(
    client, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload()
    del data["nom"]
    response = client.post(
        "/api/produits",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json["error"] == "Données invalides"
    assert "nom" in response.json["details"]


def test_products_store_negative_price(
    client, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload(prix=-5)
    response = client.post(
        "/api/produits",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "prix" in response.json["details"]


def test_products_store_unknown_field(
    client, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload(role="admin")
    response = client.post(
        "/api/produits",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "role" in response.json["details"]


def test_products_update_requires_authentication(
    client, products, make_product_payload
):
    response = client.put("/api/produits/1", json=make_product_payload())
    assert response.status_code == 401


def test_products_update_forbidden_for_client(
    client, products, client_user, make_token, make_product_payload
):
    token = make_token(client_user)
    response = client.put(
        "/api/produits/1",
        json=make_product_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_products_update_ok_for_admin(
    client, products, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload()
    response = client.put(
        "/api/produits/1",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    json = response.json
    assert json["id"] == 1
    assert json["nom"] == data["nom"]
    assert json["prix"] == data["prix"]

    product = db.session.get(Product, 1)
    assert product.name == data["nom"]
    assert product.price_cents == 99990
    assert product.stock_quantity == data["quantite_stock"]


def test_products_update_404(client, admin_user, make_token, make_product_payload):
    token = make_token(admin_user)
    response = client.put(
        "/api/produits/9999",
        json=make_product_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json["error"] == "Produit introuvable"


def test_products_update_unknown_category(
    client, products, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload(categorie_id=9999)
    response = client.put(
        "/api/produits/1",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert response.json["error"] == "Catégorie introuvable"


def test_products_update_missing_field(
    client, products, admin_user, make_token, make_product_payload
):
    token = make_token(admin_user)
    data = make_product_payload()
    del data["nom"]
    response = client.put(
        "/api/produits/1",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    assert "nom" in response.json["details"]


def test_products_delete_requires_authentication(client, products):
    response = client.delete("/api/produits/1")
    assert response.status_code == 401


def test_products_delete_forbidden_for_client(
    client, products, client_user, make_token
):
    token = make_token(client_user)
    response = client.delete(
        "/api/produits/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_products_delete_ok_for_admin(client, products, admin_user, make_token):
    token = make_token(admin_user)
    response = client.delete(
        "/api/produits/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.data == b""
    assert db.session.get(Product, 1) is None


def test_products_delete_404(client, admin_user, make_token):
    token = make_token(admin_user)
    response = client.delete(
        "/api/produits/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json["error"] == "Produit introuvable"
