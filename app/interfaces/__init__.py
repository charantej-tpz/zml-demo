"""
Interfaces package for service layer abstractions.

Contains abstract base classes that define contracts for services.
Following the Dependency Inversion Principle, services depend on
these abstractions rather than concrete implementations.
"""

from app.interfaces.authentication import IAuthenticationService

__all__ = ["IAuthenticationService"]
