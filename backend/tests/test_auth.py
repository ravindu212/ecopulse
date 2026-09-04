from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User


REGISTRATION = {
    "name": "Ari Green",
    "email": "Ari.Green@Example.com ",
    "password": "correct-horse-battery-staple",
}


def register(client):
    return client.post("/api/v1/auth/register", json=REGISTRATION)


def test_successful_registration_returns_safe_user_and_token(client):
    response = register(client)

    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["email"] == "ari.green@example.com"
    assert "password_hash" not in payload["user"]
    assert "password" not in payload["user"]


def test_duplicate_email_registration_is_rejected(client):
    assert register(client).status_code == 201

    duplicate = client.post(
        "/api/v1/auth/register",
        json={**REGISTRATION, "email": "ari.green@example.com"},
    )

    assert duplicate.status_code == 409


def test_password_is_hashed_not_plaintext(client, db_connection):
    assert register(client).status_code == 201

    stored_password_hash = db_connection.execute(
        select(User.password_hash).where(User.email == "ari.green@example.com")
    ).scalar_one()

    assert stored_password_hash != REGISTRATION["password"]
    assert stored_password_hash.startswith("$argon2")


def test_successful_login(client):
    assert register(client).status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ARI.GREEN@example.com", "password": REGISTRATION["password"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert "password_hash" not in response.json()["user"]


def test_login_rejects_incorrect_password(client):
    assert register(client).status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"email": REGISTRATION["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_login_rejects_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_authenticated_me_returns_safe_user(client):
    registration = register(client)
    token = registration.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "ari.green@example.com"
    assert "password_hash" not in response.json()


def test_me_rejects_missing_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_expired_token(client):
    expired_token = jwt.encode(
        {
            "sub": "00000000-0000-0000-0000-000000000000",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
