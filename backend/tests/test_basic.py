import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.database import get_db, Base, engine

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_authorize_page(client):
    response = await client.get("/authorize?client_id=frontend_client&response_type=code&redirect_uri=http://localhost:5173/callback")
    assert response.status_code == 200
    assert "<form" in response.text
