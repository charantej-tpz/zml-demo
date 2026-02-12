"""
Unit tests for Vitals Service.
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestVitalsService:
    """Test suite for VitalsService."""

    @pytest.fixture
    def mock_vitals_repo(self):
        """Mock vitals repository."""
        mock = AsyncMock()
        mock.update_user_vitals.return_value = None
        return mock

    @pytest.fixture
    def vitals_service(self, mock_vitals_repo):
        """Create a VitalsService with mocked repository."""
        from app.services.vitals import VitalsService

        return VitalsService(mock_vitals_repo)

    @pytest.mark.asyncio
    async def test_update_vitals_success(self, vitals_service, mock_vitals_repo):
        """Test successful vitals update."""
        user_id = "user123"

        with patch("time.time", return_value=1234567890):
            with patch("random.randint", side_effect=[75, 120]):
                result = await vitals_service.update_vitals(user_id)

                assert result["status"] == "updated"
                assert result["user_id"] == user_id
                assert result["heartrate"] == 75
                assert result["blood_pressure"] == 120
                mock_vitals_repo.update_user_vitals.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_vitals_low_heartrate(self, vitals_service, mock_vitals_repo):
        """Test vitals update with low heartrate sets status to 'Low'."""
        user_id = "user123"

        with patch("time.time", return_value=1234567890):
            with patch("random.randint", side_effect=[50, 120]):  # Low heartrate
                _ = await vitals_service.update_vitals(user_id)

                # Verify repository was called with correct status
                call_args = mock_vitals_repo.update_user_vitals.call_args[0]
                vitals_data = call_args[1]
                assert vitals_data["heart_rate"]["status"] == "Low"

    @pytest.mark.asyncio
    async def test_update_vitals_normal_heartrate(self, vitals_service, mock_vitals_repo):
        """Test vitals update with normal heartrate sets status to 'Normal'."""
        user_id = "user123"

        with patch("time.time", return_value=1234567890):
            with patch("random.randint", side_effect=[75, 120]):  # Normal heartrate
                _ = await vitals_service.update_vitals(user_id)

                call_args = mock_vitals_repo.update_user_vitals.call_args[0]
                vitals_data = call_args[1]
                assert vitals_data["heart_rate"]["status"] == "Normal"

    @pytest.mark.asyncio
    async def test_update_vitals_high_blood_pressure(self, vitals_service, mock_vitals_repo):
        """Test vitals update with high blood pressure sets status to 'Watch'."""
        user_id = "user123"

        with patch("time.time", return_value=1234567890):
            with patch("random.randint", side_effect=[75, 140]):  # High blood pressure
                _ = await vitals_service.update_vitals(user_id)

                call_args = mock_vitals_repo.update_user_vitals.call_args[0]
                vitals_data = call_args[1]
                assert vitals_data["blood_pressure"]["status"] == "Watch"

    @pytest.mark.asyncio
    async def test_update_vitals_normal_blood_pressure(self, vitals_service, mock_vitals_repo):
        """Test vitals update with normal blood pressure sets status to 'Normal'."""
        user_id = "user123"

        with patch("time.time", return_value=1234567890):
            with patch("random.randint", side_effect=[75, 120]):  # Normal blood pressure
                _ = await vitals_service.update_vitals(user_id)

                call_args = mock_vitals_repo.update_user_vitals.call_args[0]
                vitals_data = call_args[1]
                assert vitals_data["blood_pressure"]["status"] == "Normal"

    @pytest.mark.asyncio
    async def test_update_vitals_includes_timestamp(self, vitals_service, mock_vitals_repo):
        """Test vitals update includes timestamp in data."""
        user_id = "user123"
        mock_timestamp = 1234567890

        with patch("time.time", return_value=mock_timestamp):
            with patch("random.randint", side_effect=[75, 120]):
                await vitals_service.update_vitals(user_id)

                call_args = mock_vitals_repo.update_user_vitals.call_args[0]
                vitals_data = call_args[1]
                assert vitals_data["heart_rate"]["updated_at"] == mock_timestamp
                assert vitals_data["blood_pressure"]["updated_at"] == mock_timestamp

    @pytest.mark.asyncio
    async def test_update_vitals_repository_error(self, vitals_service, mock_vitals_repo):
        """Test database error handling."""
        user_id = "user123"

        mock_vitals_repo.update_user_vitals.side_effect = Exception("Database error")

        from app.core.exceptions import DatabaseError

        with pytest.raises(DatabaseError):
            await vitals_service.update_vitals(user_id)

    @pytest.mark.asyncio
    async def test_update_vitals_random_range(self, vitals_service):
        """Test that random values are generated within expected range."""
        user_id = "user123"

        with patch("random.randint") as mock_randint:
            mock_randint.return_value = 500

            with patch("time.time", return_value=1234567890):
                await vitals_service.update_vitals(user_id)

                # Verify random.randint was called with correct range
                assert mock_randint.call_count == 2
                mock_randint.assert_called_with(1, 1000)
