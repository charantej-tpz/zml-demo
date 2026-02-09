"""
Base repository interface.

Defines the generic contract for all repository operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    Generic repository interface defining common CRUD operations.

    All domain-specific repositories should extend this interface.
    This follows the Dependency Inversion Principle - services depend
    on this abstraction, not concrete implementations.
    """

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get a record by ID."""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100) -> List[T]:
        """Get all records with optional limit."""
        pass

    @abstractmethod
    async def create(self, data: Dict[str, Any], id: Optional[str] = None) -> str:
        """Create a new record. Returns the ID."""
        pass

    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> None:
        """Update an existing record."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete a record."""
        pass

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if a record exists."""
        pass
