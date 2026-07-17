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

## Configuration

L'application lit sa configuration depuis un fichier `.env` (variables préfixées
`FLASK_`). Ce fichier n'est **pas versionné** : créez-le à partir du modèle fourni
et renseignez la clé secrète utilisée pour signer les JWT.

```bash
cp .env.example .env
```

Éditez ensuite `.env` pour donner une valeur à `FLASK_JWT_SECRET`, par exemple :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
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

Le seed crée le catalogue (catégories + produits), deux comptes de démonstration,
et deux commandes de test rattachées au compte client (une `en_attente`, une
`annulée`) pour que les routes de commandes renvoient immédiatement des données :

| Rôle | Email | Mot de passe |
|---|---|---|
| Administrateur | `admin@digimarket.fr` | `admin1234!` |
| Client | `client@digimarket.fr` | `client1234!` |

Connectez-vous via `POST /api/auth/login` avec l'un de ces comptes pour obtenir un
JWT et accéder aux routes protégées (le compte administrateur débloque la gestion
du catalogue et des commandes).

## Documentation de l'API

Base URL : `http://localhost:5000`. Requêtes et réponses en JSON.

### Authentification

L'authentification repose sur des **JWT**. On obtient un jeton via `POST /api/auth/login`,
puis on l'envoie sur les routes protégées dans l'en-tête :

```
Authorization: Bearer <token>
```

Deux rôles : `client` et `admin`. Un jeton absent ou invalide renvoie `401`, un accès
interdit pour le rôle renvoie `403`.

### Format des erreurs

Toutes les erreurs suivent le même contrat :

```json
{ "error": "Message lisible" }
```

Les erreurs de validation ajoutent le détail par champ sous `details` :

```json
{ "error": "Données invalides", "details": { "mot_de_passe": ["8 caractères minimum"] } }
```

### Routes

| Méthode | Route | Accès | Description |
|---|---|---|---|
| POST | `/api/auth/register` | public | Créer un compte client |
| POST | `/api/auth/login` | public | Obtenir un JWT |
| | | | |
| GET | `/api/categories` | public | Lister les catégories |
| | | | |
| GET | `/api/produits` | public | Lister les produits (pagination + recherche) |
| GET | `/api/produits/{id}` | public | Détail d'un produit |
| POST | `/api/produits` | admin | Créer un produit |
| PUT | `/api/produits/{id}` | admin | Modifier un produit |
| DELETE | `/api/produits/{id}` | admin | Supprimer un produit |
| | | | |
| GET | `/api/commandes` | authentifié | Lister les commandes (admin : toutes · client : les siennes) |
| GET | `/api/commandes/{id}` | propriétaire / admin | Détail d'une commande (sans les lignes) |
| GET | `/api/commandes/{id}/lignes` | propriétaire / admin | Lignes d'une commande |
| POST | `/api/commandes` | client | Créer une commande |
| PATCH | `/api/commandes/{id}` | admin | Changer le statut d'une commande |

> `GET /api/commandes/{id}` renvoie l'**enveloppe** de la commande (statut, adresse,
> propriétaire) ; le **contenu** (produits, quantités, prix) s'obtient via
> `GET /api/commandes/{id}/lignes`. Chaque route a une responsabilité distincte.

### Exemples

**Inscription** — `POST /api/auth/register`
```json
{ "email": "jean@example.fr", "mot_de_passe": "Secret12!", "nom": "Jean Client" }
```
→ `201` avec l'utilisateur créé.

**Connexion** — `POST /api/auth/login`
```json
{ "email": "client@digimarket.fr", "mot_de_passe": "client1234!" }
```
→ `200` `{ "token": "<jwt>" }`.

**Lister les produits** — `GET /api/produits?page=1&per_page=10&search=clavier`
```json
{ "items": [ { "id": 3, "nom": "Logitech G Pro Clavier", "description": "…",
  "categorie": { "id": 2, "nom": "Périphériques" }, "prix": 12.9,
  "quantite_stock": 30, "date_creation": "…" } ],
  "page": 1, "per_page": 10, "total": 1, "pages": 1 }
```

**Créer une commande** — `POST /api/commandes` (client, JWT requis)
```json
{ "adresse_livraison": "12 rue de la Paix, 75002 Paris",
  "produits": [ { "produit_id": 1, "quantite": 2 }, { "produit_id": 3, "quantite": 1 } ] }
```
→ `201` avec la commande et ses lignes. La disponibilité du stock est vérifiée
(`422` si un produit manque) ; le **stock n'est pas décrémenté** à la création.

**Changer le statut** — `PATCH /api/commandes/{id}` (admin)
```json
{ "statut": "validée" }
```
→ `200` avec la commande mise à jour.

### Statuts de commande

Valeurs possibles : `en_attente`, `validée`, `expédiée`, `annulée`. Les changements
suivent une **machine à états** — seules ces transitions sont autorisées (sinon `422`) :

| Depuis | Vers |
|---|---|
| `en_attente` | `validée`, `annulée` |
| `validée` | `expédiée`, `annulée` |
| `expédiée` | *(terminal)* |
| `annulée` | *(terminal)* |

Effet sur le stock :
- `en_attente → validée` : le stock est **décrémenté** (contrôle tout-ou-rien ;
  `422` et aucune modification si une ligne manque de stock) ;
- `validée → annulée` : le stock est **re-crédité** ;
- toutes les autres transitions ne touchent pas au stock.

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

Sans uv, pour lancer les tests, installez le runtime **et** les outils de dev
(`requirements-dev.txt` ne contient que les outils de dev, pas les dépendances
d'exécution) :

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
