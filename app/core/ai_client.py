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
    def __init__(self, url, api_key: str = "", handler_link: str = "http://127.0.0.1:21489"):
        self.url = url
        self.api_key = api_key
        self.handler_link = handler_link

        self._create_processors()

    def _create_processors(self):
        self.ai_consulter = AIConsulterProcessor(api_key=self.api_key, handler_link=self.handler_link)
        self.translator = TranslatorProcessor(api_key=self.api_key, handler_link=self.handler_link)
        self.tts = AsyncTextToSpeechMMLM(api_key=self.api_key, handler_link=self.handler_link)

    def set_url(self, url):
        self.url = url

    def update_api_settings(self, api_key: str, handler_link: str):
        self.api_key = api_key
        self.handler_link = handler_link
        self._create_processors()

    @safe_request
    def ask(self, chat: list[dict], model_name: str = "gpt-5.4-mini") -> str:
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
            model_name: str = "gpt-4o-mini-tts",
    ) -> list[str]:
        if isinstance(texts, str):
            texts = [texts]

        payload = TTSInputModel(
            texts=texts,
            voice=voice,
            model_name=model_name,
        )
        response = asyncio.run(self.tts(body=payload))
        return response.audio_base64

    @safe_request
    def translate_text(
            self,
            text: str,
            target_language: str = "ru",
            model_name: str = "gpt-5.4-nano",
    ) -> str:
        payload = TranslatorInputModel(
            text=text,
            target_language=target_language,
            model_name=model_name,
        )
        response = asyncio.run(self.translator(body=payload))
        return response.text
