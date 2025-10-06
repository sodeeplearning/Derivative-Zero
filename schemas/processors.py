from typing import Optional, List, Any

from pydantic import BaseModel

from .base import TextModel


class AIConsulterInputModel(BaseModel):
    context: str
    question: str
    images: Optional[List[str]]


class AIConsulterOutputModel(TextModel):
    ...


class TranslatorInputModel(TextModel):
    target_language: str


class TranslatorOutputModel(TextModel):
    ...
