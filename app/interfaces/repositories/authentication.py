from abc import ABC, abstractmethod
from typing import Any, Dict


class IAuthenticationRepository(ABC):
    """Interface for authentication repository operations."""

    @abstractmethod
    async def register_user(self, uid: str, data: Dict[str, Any]) -> None:
        """Register a new user with the given username and password."""
        pass
