"""
Unit tests for Medical Info Service.
"""

from unittest.mock import AsyncMock

import pytest


class TestMedicalInfoService:
    """Test suite for MedicalInfoService."""

    @pytest.fixture
    def mock_medical_repo(self):
        """Mock medical info repository."""
        mock = AsyncMock()
        mock.get_user_medical_info.return_value = None
        mock.set_user_medical_info.return_value = None
        return mock

    @pytest.fixture
    def medical_service(self, mock_medical_repo):
        """Create a MedicalInfoService with mocked repository."""
        from app.services.medical_info import MedicalInfoService

        return MedicalInfoService(mock_medical_repo)

    @pytest.mark.asyncio
    async def test_get_medical_info_success(self, medical_service, mock_medical_repo):
        """Test successful retrieval of medical info."""
        user_id = "user123"
        mock_data = {"height": 175.5, "weight": 70.0}
        mock_medical_repo.get_user_medical_info.return_value = mock_data

        result = await medical_service.get_medical_info(user_id)

        assert result is not None
        assert result["user_id"] == user_id
        assert result["height"] == 175.5
        assert result["weight"] == 70.0
        mock_medical_repo.get_user_medical_info.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_medical_info_not_found(self, medical_service, mock_medical_repo):
        """Test when medical info is not found."""
        user_id = "user123"
        mock_medical_repo.get_user_medical_info.return_value = None

        result = await medical_service.get_medical_info(user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_medical_info_repository_error(self, medical_service, mock_medical_repo):
        """Test database error handling during get."""
        user_id = "user123"
        mock_medical_repo.get_user_medical_info.side_effect = Exception("Database error")

        from app.core.exceptions import DatabaseError

        with pytest.raises(DatabaseError):
            await medical_service.get_medical_info(user_id)

    @pytest.mark.asyncio
    async def test_set_medical_info_success(self, medical_service, mock_medical_repo):
        """Test successful setting of medical info."""
        user_id = "user123"
        height = 180.0
        weight = 75.5

        result = await medical_service.set_medical_info(user_id, height, weight)

        assert result["user_id"] == user_id
        assert result["height"] == height
        assert result["weight"] == weight
        mock_medical_repo.set_user_medical_info.assert_called_once_with(
            user_id, {"height": height, "weight": weight}
        )

    @pytest.mark.asyncio
    async def test_set_medical_info_different_values(self, medical_service, mock_medical_repo):
        """Test setting medical info with different values."""
        test_cases = [
            ("user1", 170.0, 65.0),
            ("user2", 180.5, 80.0),
            ("user3", 165.0, 55.5),
        ]

        for user_id, height, weight in test_cases:
            mock_medical_repo.reset_mock()

            result = await medical_service.set_medical_info(user_id, height, weight)

            assert result["user_id"] == user_id
            assert result["height"] == height
            assert result["weight"] == weight

    @pytest.mark.asyncio
    async def test_set_medical_info_repository_error(self, medical_service, mock_medical_repo):
        """Test database error handling during set."""
        user_id = "user123"
        height = 175.0
        weight = 70.0

        mock_medical_repo.set_user_medical_info.side_effect = Exception("Database error")

        from app.core.exceptions import DatabaseError

        with pytest.raises(DatabaseError):
            await medical_service.set_medical_info(user_id, height, weight)

    @pytest.mark.asyncio
    async def test_set_medical_info_with_decimals(self, medical_service, mock_medical_repo):
        """Test setting medical info with decimal precision."""
        user_id = "user123"
        height = 175.75
        weight = 70.25

        result = await medical_service.set_medical_info(user_id, height, weight)

        assert result["height"] == height
        assert result["weight"] == weight

    @pytest.mark.asyncio
    async def test_get_medical_info_preserves_user_id(self, medical_service, mock_medical_repo):
        """Test that user_id is preserved in returned data."""
        user_id = "user123"
        mock_data = {"height": 175.5, "weight": 70.0}
        mock_medical_repo.get_user_medical_info.return_value = mock_data

        result = await medical_service.get_medical_info(user_id)

        assert result["user_id"] == user_id
