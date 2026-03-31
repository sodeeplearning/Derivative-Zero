import asyncio
import json
from typing import Callable

from processors.ai_consulter import AIConsulterProcessor
from processors.translator import TranslatorProcessor
from processors.tts import AsyncTextToSpeechMMLM

from schemas.processors import (
    AIConsulterInputModel,
    TranslatorInputModel,
    TTSInputModel,
)


class AIClientError(Exception):
    ...


def safe_request(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            raise AIClientError(f"Ошибка: {e}")

    return wrapper


class AIClient:
    def __init__(self, url):
        self.url = url

        self.ai_consulter = AIConsulterProcessor()
        self.translator = TranslatorProcessor()
        self.tts = AsyncTextToSpeechMMLM()

    def set_url(self, url):
        self.url = url

    @safe_request
    def ask(self, chat: list[dict], model_name: str = "gpt-5-mini") -> str:
        payload = AIConsulterInputModel(
            chat=json.dumps(chat),
            model_name=model_name,
        )
        response = asyncio.run(self.ai_consulter(body=payload))
        return response.text

    @safe_request
    def get_speech(
            self,
            texts: str | list[str],
            voice: str = "coral",
    ) -> list[str]:
        if isinstance(texts, str):
            texts = [texts]

        payload = TTSInputModel(
            texts=texts,
            voice=voice,
        )
        response = asyncio.run(self.tts(body=payload))
        return response.audio_base64

    @safe_request
    def translate_text(self, text: str, target_language: str = "ru") -> str:
        payload = TranslatorInputModel(
            text=text,
            target_language=target_language,
        )
        response = asyncio.run(self.translator(body=payload))
        return response.text
