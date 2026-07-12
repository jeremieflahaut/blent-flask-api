# DigiMarket API

[![CI](https://github.com/jeremieflahaut/blent-flask-api/actions/workflows/ci.yml/badge.svg)](https://github.com/jeremieflahaut/blent-flask-api/actions/workflows/ci.yml)

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

## Initialiser la base de données

La base SQLite n'est pas versionnée : on la (re)génère avec un jeu de données de
test via le script de seed (recrée la base à zéro à chaque exécution).

```bash
python seed.py                  # ou : uv run python seed.py
```

Le seed crée le catalogue (catégories + produits) et deux comptes de démonstration :

| Rôle | Email | Mot de passe |
|---|---|---|
| Administrateur | `admin@digimarket.fr` | `admin1234!` |
| Client | `client@digimarket.fr` | `client1234!` |

Connectez-vous via `POST /api/auth/login` avec l'un de ces comptes pour obtenir un
JWT et accéder aux routes protégées (le compte administrateur débloque la gestion
du catalogue et des commandes).

## Conventions

- **Dates en UTC naïf.** Toutes les colonnes datetime (`created_at`, …) sont
  stockées en **UTC sans information de fuseau** (`tzinfo` retiré). SQLite ne
  conservant pas le fuseau, on évite ainsi tout mélange naïf/aware. Toute
  comparaison de date doit donc se faire avec un « maintenant » UTC naïf :
  `datetime.now(timezone.utc).replace(tzinfo=None)`. La conversion vers l'heure
  locale se fait uniquement à l'affichage.
- **Règles de mot de passe** (validées à l'inscription, `POST /api/auth/register`) :
  - **8 caractères minimum**,
  - au moins **un chiffre**,
  - au moins **un caractère spécial** (non alphanumérique).

  Un mot de passe non conforme renvoie un `422` avec le détail des règles non
  respectées sous la clé `details`.

## Choix techniques

L'API suit la structure de données de référence du projet, avec deux écarts
**délibérés** qui vont au-delà du schéma imposé sans en modifier le contrat :

- **Catégorie modélisée comme une table liée** (et non un simple champ texte sur
  le produit). La catégorie est une entité à part entière (`Category`), reliée aux
  produits par une clé étrangère. Cela évite de dupliquer les libellés, garantit
  leur cohérence, et permet d'exposer l'endpoint `GET /api/categories` pour la
  navigation dans le catalogue.
- **Prix stockés en centimes** (`Integer`) plutôt qu'en flottant. On n'utilise
  jamais de `float` pour de la monnaie (erreurs d'arrondi : `0.1 + 0.2 != 0.3`).
  Le montant est stocké en centimes et converti en euros à l'affichage — le
  contrat de l'API reste un prix en euros, seule l'implémentation interne change.

Par ailleurs, conformément à la référence, le **prix unitaire est figé sur la ligne
de commande** (`prix_unitaire`) au moment de la commande : l'historique reste exact
même si le prix du produit évolue ensuite.

## Développement

Outillage qualité : [black](https://black.readthedocs.io/) (formatage) et
[flake8](https://flake8.pycqa.org/) (lint), exécutés à chaque commit via
[pre-commit](https://pre-commit.com/).

```bash
uv sync                        # installe aussi les outils de dev
uv run pre-commit install      # active les hooks git
uv run black .                 # formater
uv run flake8                  # linter
uv run pytest                  # lancer les tests
```
