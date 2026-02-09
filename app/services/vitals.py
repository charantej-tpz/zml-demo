"""
Vitals service module.

Implements vitals business logic following SOLID principles:
- Single Responsibility: Only handles business logic (status calculation)
- Dependency Inversion: Depends on IVitalsRepository abstraction
"""

import logging
import random
import time
from typing import Any, Dict

from app.core.exceptions import DatabaseError
from app.interfaces.repositories.vitals import IVitalsRepository
from app.interfaces.vitals import IVitalsService

logger = logging.getLogger(__name__)


class VitalsService(IVitalsService):
    """
    Concrete implementation of vitals service.

    Handles vitals business logic. Data access is delegated to the repository.
    """

    def __init__(self, repo: IVitalsRepository) -> None:
        """
        Initialize the vitals service.

        Args:
            repo: Vitals repository for data operations.
        """
        self.repo = repo

    async def update_vitals(self, user_id: str) -> Dict[str, Any]:
        """
        Update user vitals in the database with random values.

        Business Logic:
        - Generates random heartrate and blood_pressure (1-1000)
        - Calculates status based on values
        - Delegates storage to repository

        Args:
            user_id: The user's ID.

        Returns:
            Update status response with generated values.

        Raises:
            DatabaseError: If database operation fails.
        """
        try:
            logger.info(f"Updating vitals for user: {user_id}")

            # Business logic: generate values and calculate status
            timestamp = int(time.time())
            heartrate = random.randint(1, 1000)  # nosec B311 - demo data only
            blood_pressure = random.randint(1, 1000)  # nosec B311 - demo data only

            vitals_data = {
                "heart_rate": {
                    "value": heartrate,
                    "unit": "bpm",
                    "status": "Low" if heartrate < 60 else "Normal",
                    "updated_at": timestamp,
                },
                "blood_pressure": {
                    "systolic": blood_pressure,
                    "unit": "mmHg",
                    "status": "Watch" if blood_pressure > 130 else "Normal",
                    "updated_at": timestamp,
                },
            }

            # Delegate to repository for data access
            await self.repo.update_user_vitals(user_id, vitals_data)

            logger.info(f"Vitals updated successfully for user: {user_id}")
            return {
                "status": "updated",
                "user_id": user_id,
                "heartrate": heartrate,
                "blood_pressure": blood_pressure,
            }

        except DatabaseError:
            raise
        except Exception as e:
            logger.exception(f"Error updating vitals for user {user_id}: {e}")
            raise DatabaseError(detail=f"Failed to update vitals: {e}") from e
