"""
Authentication service interface.

Defines the contract for authentication operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IAuthenticationService(ABC):
    """
    Interface for authentication operations.

    Follows Interface Segregation Principle - focused only on auth operations.
    Enables Dependency Inversion - clients depend on this abstraction.
    """

    @abstractmethod
    async def register(self, token: str) -> Dict[str, Any]:
        """
        Register a new user with the provided token.

        Args:
            token: Firebase ID token to verify.

        Returns:
            Decoded token containing user information.
        """
        pass

    @abstractmethod
    async def get_me(self, token: str) -> Dict[str, Any]:
        """
        Get the current user's information from the token.

        Args:
            token: Firebase ID token to decode.

        Returns:
            Full decoded token with user information.
        """
        pass
