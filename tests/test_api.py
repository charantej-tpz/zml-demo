"""
Tests for API endpoints (root and docs).
"""

import pytest


class TestRootEndpoints:
    """Test suite for root API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "ZML API" in data["name"]
        assert "version" in data
        assert "environment" in data

    def test_docs_available_in_debug(self, client):
        """Test OpenAPI docs are available in debug mode."""
        response = client.get("/docs")
        
        # Should redirect or return docs page
        assert response.status_code in [200, 307]

    def test_openapi_schema(self, client):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestAPIPrefix:
    """Test suite for API prefix routing."""

    def test_api_v1_health(self, client):
        """Test health endpoint is under /api/v1 prefix."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200

    def test_invalid_path_returns_404(self, client):
        """Test invalid paths return 404."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
