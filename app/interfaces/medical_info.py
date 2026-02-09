"""
Medical info service interface.

Defines the contract for medical info operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IMedicalInfoService(ABC):
    """Interface for medical info service operations."""

    @abstractmethod
    async def get_medical_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get medical info for a user."""
        pass

    @abstractmethod
    async def set_medical_info(self, user_id: str, height: float, weight: float) -> Dict[str, Any]:
        """Set medical info for a user."""
        pass
