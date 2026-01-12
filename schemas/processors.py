from typing import Optional, List, Literal

from pydantic import BaseModel, Field

from .base import TextModel


class AIConsulterInputModel(BaseModel):
    context: str
    question: str
    images: Optional[List[str]]
    convert_to_html: Optional[bool] = Field(default=True)


class AIConsulterOutputModel(TextModel):
    ...


class TranslatorInputModel(TextModel):
    target_language: str


class TranslatorOutputModel(TextModel):
    ...


class TTSInputModel(BaseModel):
    texts: List[str]
    voice: str
    tts_provider: Literal["yandex", "openai"]


class TTSOutputModel(BaseModel):
    audio_base64: list[str]
