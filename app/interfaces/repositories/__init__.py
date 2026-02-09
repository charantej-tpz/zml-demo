"""Repository interfaces package."""

from app.interfaces.repositories.base import IRepository
from app.interfaces.repositories.vitals import IVitalsRepository

__all__ = ["IRepository", "IVitalsRepository"]
