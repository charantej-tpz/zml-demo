"""
Vitals repository interface.

Defines the contract for vitals data operations.
"""

from abc import abstractmethod
from typing import Any, Dict

from app.interfaces.repositories.base import IRepository


class IVitalsRepository(IRepository[Dict[str, Any]]):
    """
    Interface for vitals repository operations.

    Extends IRepository with vitals-specific methods.
    """

    @abstractmethod
    async def update_user_vitals(self, user_id: str, vitals_data: Dict[str, Any]) -> None:
        """
        Update vitals for a specific user.

        Args:
            user_id: The user's ID.
            vitals_data: Dictionary containing vitals data.
        """
        pass

    @abstractmethod
    async def get_user_vitals(self, user_id: str) -> Dict[str, Any]:
        """
        Get vitals for a specific user.

        Args:
            user_id: The user's ID.

        Returns:
            Dictionary containing user's vitals data.
        """
        pass
