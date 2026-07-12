import pytest
from sqlalchemy.exc import IntegrityError
from models import db


def test_cannot_delete_category_with_products(app, products, categories):
    category = categories["laptops"]
    db.session.delete(category)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_categories_index_empty(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert response.json == []


def test_categories_index(client, categories):
    response = client.get("/api/categories")
    assert response.status_code == 200

    json = response.json
    assert len(json) == 2

    for categorie in json:
        assert categorie["id"] is not None
        assert categorie["nom"] is not None
        assert categorie["date_creation"] is not None


def test_categories_index_sorted_by_name(client, categories):
    response = client.get("/api/categories")
    assert response.status_code == 200

    noms = [categorie["nom"] for categorie in response.json]
    assert noms == ["Ordinateurs portables", "Périphériques"]
