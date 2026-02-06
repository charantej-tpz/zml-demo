"""
Tests for health check endpoints.
"""

import pytest


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check returns 200."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_health_check_returns_version(self, client):
        """Test health check returns app version."""
        response = client.get("/api/v1/health")
        
        data = response.json()
        assert data["version"] == "0.1.0"
        assert data["environment"] == "development"

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "firestore" in data["checks"]
