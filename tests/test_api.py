"""Tests for API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_chat_endpoint(client):
    """Test chat endpoint."""
    # TODO: Implement when endpoint is ready
    pass


@pytest.mark.asyncio
async def test_status_endpoint(client):
    """Test status endpoint."""
    # TODO: Implement when endpoint is ready
    pass
