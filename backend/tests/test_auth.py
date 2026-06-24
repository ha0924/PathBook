"""用户认证模块 - 关键路径测试."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """注册接口测试."""

    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "password": "test123456"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "testuser"
        assert "id" in data["data"]

    async def test_register_duplicate_username(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={"username": "dupuser", "password": "test123456"},
        )
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "dupuser", "password": "another123"},
        )
        assert resp.status_code == 409
        assert resp.json()["code"] == 40001  # USER_ALREADY_EXISTS

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "shortpwd", "password": "12345"},
        )
        assert resp.status_code == 422  # Pydantic validation (min_length=6)

    async def test_register_username_too_short(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "ab", "password": "test123456"},
        )
        assert resp.status_code == 422  # Pydantic validation


@pytest.mark.asyncio
class TestLogin:
    """登录接口测试."""

    async def test_login_success(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={"username": "loginuser", "password": "test123456"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "loginuser", "password": "test123456"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={"username": "wrongpwd", "password": "test123456"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "wrongpwd", "password": "wrongpassword"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == 40101  # AUTH_INVALID_CREDENTIALS

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "noone", "password": "whatever123"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == 40101


@pytest.mark.asyncio
class TestMe:
    """获取当前用户接口测试."""

    async def test_me_success(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={"username": "meuser", "password": "test123456"},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "meuser", "password": "test123456"},
        )
        token = login_resp.json()["data"]["access_token"]

        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "meuser"
        assert data["data"]["is_active"] is True

    async def test_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == 40103  # AUTH_TOKEN_INVALID
