"""
Repositories module for database operations.

Repositories encapsulate all database queries and operations,
providing a clean abstraction layer between the service layer and databases.

- BaseRepository: For Firestore operations
- RealtimeBaseRepository: For Firebase Realtime Database operations
"""

from app.repositories.base import BaseRepository
from app.repositories.realtime_base import RealtimeBaseRepository

__all__ = ["BaseRepository", "RealtimeBaseRepository"]
