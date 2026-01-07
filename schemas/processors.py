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


class TTSInputModel(TextModel):
    voice: Literal["male", "female"] = Field(default="male")


class TTSOutputModel(BaseModel):
    audio_base64: str
