from typing import Optional, List

from pydantic import BaseModel


class TextModel(BaseModel):
    text: str


class AIConsulterInputModel(BaseModel):
    context: str
    question: str
    images: Optional[List[str]]


class TranslatorInputModel(TextModel):
    target_language: str
