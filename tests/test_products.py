def test_products_index(client):
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
        assert produit["name"] is not None
        assert produit["description"] is not None
        assert produit["price"] is not None
        assert produit["stock"] is not None


def test_products_show(client):
    response = client.get("/api/produits/1")
    assert response.status_code == 200

    produit = response.json

    assert produit["id"] is not None
    assert produit["name"] is not None
    assert produit["name"] == "MSI Pro 16 Flex"
    assert produit["description"] is not None
    assert produit["price"] is not None
    assert produit["stock"] is not None


def test_products_show_404(client):
    response = client.get("/api/produits/5")
    assert response.status_code == 404
    assert response.json["error"] == "Product not found"
