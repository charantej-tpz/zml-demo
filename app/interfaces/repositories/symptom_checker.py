from abc import ABC, abstractmethod


class ISymptomCheckerRepository(ABC):
    """Interface for symptom checker repository operations."""

    @abstractmethod
    async def start_conversation(self) -> str:
        """Check symptoms and return possible conditions."""
        pass

    @abstractmethod
    def create_user_message(self, conversation_id: str, message: list[str]) -> None:
        """Create a user message in the conversation."""
        pass

    @abstractmethod
    def create_agent_message(
        self, conversation_id: str, message: list[str], response_type: str
    ) -> None:
        """Create a bot message in the conversation."""
        pass
