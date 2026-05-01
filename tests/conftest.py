"""pytest configuration and fixtures."""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def app():
    """FastAPI test app fixture."""
    from app.main import app
    return app


@pytest.fixture
async def client():
    """FastAPI test client fixture."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
