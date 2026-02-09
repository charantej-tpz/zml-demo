"""
Medical info repository interface.

Defines the contract for medical info data operations.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional

from app.interfaces.repositories.base import IRepository


class IMedicalInfoRepository(IRepository[Dict[str, Any]]):
    """Interface for medical info repository operations."""

    @abstractmethod
    async def get_user_medical_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get medical info for a specific user."""
        pass

    @abstractmethod
    async def set_user_medical_info(self, user_id: str, data: Dict[str, Any]) -> None:
        """Set medical info for a specific user."""
        pass
