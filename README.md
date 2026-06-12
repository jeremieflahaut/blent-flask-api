# DigiMarket API

API REST e-commerce (produits, commandes, utilisateurs) — Flask + SQLAlchemy + JWT.

Projet du module Python — formation Blent LLM Engineer.

## Prérequis

- Python 3.12+

## Installation

```bash
git clone https://github.com/jeremieflahaut/blent-flask-api.git
cd blent-flask-api
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Alternative si vous utilisez [uv](https://docs.astral.sh/uv/) :

```bash
uv sync
```

## Lancer l'API

```bash
flask run --debug               # ou : uv run flask run --debug
```

L'API répond sur http://localhost:5000.

## Développement

Outillage qualité : [black](https://black.readthedocs.io/) (formatage) et
[flake8](https://flake8.pycqa.org/) (lint), exécutés à chaque commit via
[pre-commit](https://pre-commit.com/).

```bash
uv sync                        # installe aussi les outils de dev
uv run pre-commit install      # active les hooks git
uv run black .                 # formater
uv run flake8                  # linter
```
