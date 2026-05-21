from httpx import AsyncClient

from tests.helpers import DEFAULT_PASSWORD, login, register_user


async def test_login_returns_token_pair(client: AsyncClient) -> None:
    await register_user(client, email="login@example.com", username="loginu")
    body = await login(client, email="login@example.com")
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_401(client: AsyncClient) -> None:
    await register_user(client, email="wp@example.com", username="wp")
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "wp@example.com", "password": "wrong-password"},
    )
    assert r.status_code == 401


async def test_login_unknown_email_401(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": DEFAULT_PASSWORD},
    )
    assert r.status_code == 401


async def test_refresh_issues_new_access(client: AsyncClient) -> None:
    await register_user(client, email="rf@example.com", username="rf")
    tokens = await login(client, email="rf@example.com")
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_refresh_rejects_access_token(client: AsyncClient) -> None:
    """Access tokens must not be usable as refresh tokens (type discriminator)."""
    await register_user(client, email="cross@example.com", username="cross")
    tokens = await login(client, email="cross@example.com")
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r.status_code == 401
