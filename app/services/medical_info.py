"""
Medical info service module.

Implements medical info business logic following SOLID principles.
"""

import logging
from typing import Any, Dict, Optional

from app.core.exceptions import DatabaseError, NotFoundError
from app.interfaces.medical_info import IMedicalInfoService
from app.interfaces.repositories.medical_info import IMedicalInfoRepository

logger = logging.getLogger(__name__)


class MedicalInfoService(IMedicalInfoService):
    """
    Concrete implementation of medical info service.

    Handles business logic for medical info operations.
    """

    def __init__(self, repo: IMedicalInfoRepository) -> None:
        """Initialize the service with repository."""
        self.repo = repo

    async def get_medical_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get medical info for a user.

        Args:
            user_id: The user's ID.

        Returns:
            Medical info dict or None if not found.
        """
        try:
            logger.info(f"Getting medical info for user: {user_id}")
            data = await self.repo.get_user_medical_info(user_id)
            if data:
                data["user_id"] = user_id
            return data
        except DatabaseError:
            raise
        except Exception as e:
            logger.exception(f"Error getting medical info for {user_id}: {e}")
            raise DatabaseError(detail=f"Failed to get medical info: {e}") from e

    async def set_medical_info(self, user_id: str, height: float, weight: float) -> Dict[str, Any]:
        """
        Set medical info for a user.

        Args:
            user_id: The user's ID.
            height: Height in cm.
            weight: Weight in kg.

        Returns:
            The saved medical info.
        """
        try:
            logger.info(f"Setting medical info for user: {user_id}")

            medical_data = {
                "height": height,
                "weight": weight,
            }

            await self.repo.set_user_medical_info(user_id, medical_data)

            logger.info(f"Medical info saved for user: {user_id}")
            return {
                "user_id": user_id,
                "height": height,
                "weight": weight,
            }

        except DatabaseError:
            raise
        except Exception as e:
            logger.exception(f"Error setting medical info for {user_id}: {e}")
            raise DatabaseError(detail=f"Failed to set medical info: {e}") from e
