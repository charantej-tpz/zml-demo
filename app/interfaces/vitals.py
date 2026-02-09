"""
Vitals service interface.

Defines the contract for vitals operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IVitalsService(ABC):
    """
    Interface for vitals operations.

    Follows Interface Segregation Principle - focused only on vitals operations.
    """

    @abstractmethod
    async def update_vitals(self, user_id: str) -> Dict[str, Any]:
        """
        Update user vitals in the database with random values.

        Args:
            user_id: The user's ID.

        Returns:
            Update status response with generated values.
        """
        pass
