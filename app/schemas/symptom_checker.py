from pydantic import BaseModel


class SymptomCheckerSubmitInput(BaseModel):
    conversation_id: str
    symptoms: list[str]
