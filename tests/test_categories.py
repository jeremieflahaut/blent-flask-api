import pytest
from sqlalchemy.exc import IntegrityError
from models import db, Category


def test_cannot_delete_category_with_products(app):
    with app.app_context():
        category = db.session.scalar(db.select(Category))
        db.session.delete(category)
        with pytest.raises(IntegrityError):
            db.session.commit()
