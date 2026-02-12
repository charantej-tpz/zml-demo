from abc import ABC, abstractmethod
from typing import Any, Dict


class ISymptomCheckerService(ABC):
    """Interface for symptom checker service operations."""

    @abstractmethod
    def init(self) -> Dict[str, Any]:
        """Start a new symptom checker conversation."""
        pass

    @abstractmethod
    def submit(self, conversation_id: str, symptoms: list[str]) -> None:
        """Submit and get Symptom from Agent."""
        pass
