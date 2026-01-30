from typing import Optional, List

from pydantic import BaseModel, Field

from .base import TextModel


class AIConsulterInputModel(BaseModel):
    chat: str
    model_name: Optional[str] = Field(default="gpt-5-mini")
    convert_to_html: Optional[bool] = Field(default=True)


class AIConsulterOutputModel(TextModel):
    ...


class TranslatorInputModel(TextModel):
    target_language: Optional[str] = Field(default="ru")


class TranslatorOutputModel(TextModel):
    ...


class TTSInputModel(BaseModel):
    texts: List[str]
    voice: str


class TTSOutputModel(BaseModel):
    audio_base64: list[str]
