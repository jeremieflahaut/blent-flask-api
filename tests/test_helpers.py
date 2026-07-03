from datetime import datetime, timedelta, timezone


def test_auth_no_token(client):
    response = client.get("/test/require-authentication")
    assert response.status_code == 401


def test_auth_bad_headers(client, client_user, make_token):
    token = make_token(client_user)
    response = client.get(
        "/test/require-authentication", headers={"Authorization": f"Basic {token}"}
    )
    assert response.status_code == 401


def test_auth_bad_token(client):
    token = "bad_token"
    response = client.get(
        "/test/require-authentication", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_auth_bad_user(client, client_user, make_token):
    token = make_token(client_user, sub="1000")
    response = client.get(
        "/test/require-authentication", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_auth_expired_token(client, client_user, make_token):
    token = make_token(client_user, exp=datetime.now(timezone.utc) - timedelta(hours=1))
    response = client.get(
        "/test/require-authentication", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_auth_validate_token(client, client_user, make_token):
    token = make_token(client_user)
    response = client.get(
        "/test/require-authentication", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["id"] == client_user.id


def test_auth_admin_forbidden(client, client_user, make_token):
    token = make_token(client_user)
    response = client.get(
        "/test/require-admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_auth_admin_required(client, admin_user, make_token):
    token = make_token(admin_user)
    response = client.get(
        "/test/require-admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
