"""
Base repository class for Firestore operations.

Provides common CRUD operations that can be extended by specific repositories.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from google.cloud.firestore_v1 import Client, DocumentSnapshot
from pydantic import BaseModel

from app.core.exceptions import DatabaseError, NotFoundError
from app.db.firestore import get_firestore_client

logger = logging.getLogger(__name__)

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Base repository providing common Firestore CRUD operations.

    Extend this class to create specific repositories for your collections.

    Example:
        class UserRepository(BaseRepository[User]):
            collection_name = "users"
            model_class = User
    """

    collection_name: str = ""
    model_class: Type[T]

    def __init__(self, db: Optional[Client] = None) -> None:
        """
        Initialize the repository.

        Args:
            db: Firestore client. If None, uses the global client.
        """
        self._db = db

    @property
    def db(self) -> Client:
        """Get the Firestore client."""
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    @property
    def collection(self):
        """Get the Firestore collection reference."""
        return self.db.collection(self.collection_name)

    def _doc_to_model(self, doc: DocumentSnapshot) -> Optional[T]:
        """
        Convert a Firestore document to a Pydantic model.

        Args:
            doc: Firestore document snapshot.

        Returns:
            Pydantic model instance or None if document doesn't exist.
        """
        if not doc.exists:
            return None

        data = doc.to_dict()
        data["id"] = doc.id
        return self.model_class(**data)

    async def get_by_id(self, doc_id: str) -> Optional[T]:
        """
        Get a document by ID.

        Args:
            doc_id: Document ID.

        Returns:
            Model instance or None if not found.
        """
        try:
            doc = self.collection.document(doc_id).get()
            return self._doc_to_model(doc)
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            raise DatabaseError(f"Failed to get document: {e}")

    async def get_by_id_or_raise(self, doc_id: str) -> T:
        """
        Get a document by ID or raise NotFoundError.

        Args:
            doc_id: Document ID.

        Returns:
            Model instance.

        Raises:
            NotFoundError: If document not found.
        """
        result = await self.get_by_id(doc_id)
        if result is None:
            raise NotFoundError(f"{self.collection_name} with ID {doc_id} not found")
        return result

    async def get_all(self, limit: int = 100) -> List[T]:
        """
        Get all documents in the collection.

        Args:
            limit: Maximum number of documents to return.

        Returns:
            List of model instances.
        """
        try:
            docs = self.collection.limit(limit).stream()
            return [self._doc_to_model(doc) for doc in docs if doc.exists]
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            raise DatabaseError(f"Failed to get documents: {e}")

    async def create(self, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """
        Create a new document.

        Args:
            data: Document data.
            doc_id: Optional document ID. If None, Firestore generates one.

        Returns:
            Document ID.
        """
        try:
            if doc_id:
                self.collection.document(doc_id).set(data)
                return doc_id
            else:
                _, doc_ref = self.collection.add(data)
                return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise DatabaseError(f"Failed to create document: {e}")

    async def update(self, doc_id: str, data: Dict[str, Any]) -> None:
        """
        Update an existing document.

        Args:
            doc_id: Document ID.
            data: Fields to update.
        """
        try:
            self.collection.document(doc_id).update(data)
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            raise DatabaseError(f"Failed to update document: {e}")

    async def delete(self, doc_id: str) -> None:
        """
        Delete a document.

        Args:
            doc_id: Document ID.
        """
        try:
            self.collection.document(doc_id).delete()
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            raise DatabaseError(f"Failed to delete document: {e}")

    async def query(
        self,
        field: str,
        operator: str,
        value: Any,
        limit: int = 100,
    ) -> List[T]:
        """
        Query documents by a field condition.

        Args:
            field: Field name to query.
            operator: Comparison operator (==, <, >, <=, >=, !=, in, etc.).
            value: Value to compare against.
            limit: Maximum number of documents to return.

        Returns:
            List of matching model instances.
        """
        try:
            docs = self.collection.where(field, operator, value).limit(limit).stream()
            return [self._doc_to_model(doc) for doc in docs if doc.exists]
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise DatabaseError(f"Failed to query documents: {e}")

    async def exists(self, doc_id: str) -> bool:
        """
        Check if a document exists.

        Args:
            doc_id: Document ID.

        Returns:
            True if document exists, False otherwise.
        """
        try:
            doc = self.collection.document(doc_id).get()
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking document existence {doc_id}: {e}")
            raise DatabaseError(f"Failed to check document existence: {e}")
