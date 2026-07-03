import pytest
from sqlalchemy.exc import IntegrityError
from models import db


def test_cannot_delete_category_with_products(app, products, categories):
    category = categories["laptops"]
    db.session.delete(category)
    with pytest.raises(IntegrityError):
        db.session.commit()
