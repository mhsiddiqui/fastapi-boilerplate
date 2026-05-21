from httpx import AsyncClient

from tests.helpers import DEFAULT_PASSWORD, auth_header, register_user


async def test_register_creates_user(client: AsyncClient) -> None:
    payload = {"email": "a@example.com", "username": "alice", "name": "Alice", "password": DEFAULT_PASSWORD}
    r = await client.post("/api/v1/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@example.com"
    assert body["username"] == "alice"
    assert body["is_active"] is True
    assert body["is_superuser"] is False
    assert "password" not in body


async def test_register_duplicate_returns_409(client: AsyncClient) -> None:
    await register_user(client, email="dup@example.com", username="dup")
    r = await client.post(
        "/api/v1/users",
        json={"email": "dup@example.com", "username": "dup", "name": "Dup", "password": DEFAULT_PASSWORD},
    )
    assert r.status_code == 409


async def test_register_password_too_short_returns_422(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/users",
        json={"email": "x@example.com", "username": "xxx", "name": "X", "password": "short"},
    )
    assert r.status_code == 422


async def test_me_requires_auth(client: AsyncClient) -> None:
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


async def test_me_returns_current_user(client: AsyncClient) -> None:
    await register_user(client, email="me@example.com", username="meuser")
    headers = await auth_header(client, email="me@example.com")
    r = await client.get("/api/v1/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"


async def test_list_users_requires_auth(client: AsyncClient) -> None:
    r = await client.get("/api/v1/users")
    assert r.status_code == 401


async def test_list_users_pagination_shape(client: AsyncClient) -> None:
    await register_user(client, email="u1@example.com", username="u1")
    await register_user(client, email="u2@example.com", username="u2")
    await register_user(client, email="u3@example.com", username="u3")
    headers = await auth_header(client, email="u1@example.com")

    r = await client.get("/api/v1/users?page=1&page_size=2", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["pages"] == 2
    assert len(body["items"]) == 2
    assert body["current"]["page"] == 1
    assert "page=1" in body["current"]["url"]
    assert body["next"]["page"] == 2
    assert "page=2" in body["next"]["url"]
    assert body["previous"] is None


async def test_list_users_last_page(client: AsyncClient) -> None:
    await register_user(client, email="u1@example.com", username="u1")
    await register_user(client, email="u2@example.com", username="u2")
    await register_user(client, email="u3@example.com", username="u3")
    headers = await auth_header(client, email="u1@example.com")

    r = await client.get("/api/v1/users?page=2&page_size=2", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["next"] is None
    assert body["previous"]["page"] == 1


async def test_update_own_user(client: AsyncClient) -> None:
    me = await register_user(client, email="own@example.com", username="own")
    headers = await auth_header(client, email="own@example.com")
    r = await client.patch(f"/api/v1/users/{me['id']}", json={"name": "Renamed"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed"


async def test_update_other_user_forbidden(client: AsyncClient) -> None:
    await register_user(client, email="a@example.com", username="aa")
    other = await register_user(client, email="b@example.com", username="bb")
    headers = await auth_header(client, email="a@example.com")
    r = await client.patch(f"/api/v1/users/{other['id']}", json={"name": "Nope"}, headers=headers)
    assert r.status_code == 403


async def test_update_rejects_unknown_field(client: AsyncClient) -> None:
    me = await register_user(client, email="strict@example.com", username="strict")
    headers = await auth_header(client, email="strict@example.com")
    r = await client.patch(
        f"/api/v1/users/{me['id']}",
        json={"is_superuser": True},  # extra="forbid" should reject this
        headers=headers,
    )
    assert r.status_code == 422
