from flask import Blueprint
from models import db, Category

categories = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories.route("", methods=["GET"])
def index():
    query = db.select(Category).order_by(Category.name)
    items = []

    for categorie in db.session.scalars(query):
        items.append(categorie.to_dict())

    return items
