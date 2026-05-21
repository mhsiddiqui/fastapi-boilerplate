"""Small helpers shared across test modules."""

from httpx import AsyncClient

DEFAULT_PASSWORD = "Str0ng!Pass"


async def register_user(
    client: AsyncClient,
    *,
    email: str = "alice@example.com",
    username: str = "alice",
    name: str = "Alice",
    password: str = DEFAULT_PASSWORD,
) -> dict:
    res = await client.post(
        "/api/v1/users",
        json={"email": email, "username": username, "name": name, "password": password},
    )
    assert res.status_code == 201, res.text
    return res.json()


async def login(client: AsyncClient, *, email: str, password: str = DEFAULT_PASSWORD) -> dict:
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()


async def auth_header(client: AsyncClient, *, email: str, password: str = DEFAULT_PASSWORD) -> dict[str, str]:
    tokens = await login(client, email=email, password=password)
    return {"Authorization": f"Bearer {tokens['access_token']}"}
