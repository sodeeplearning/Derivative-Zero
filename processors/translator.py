from aiohttp import ClientSession

import config
from .base import AbstractRemoteProcessor

from schemas.processors import TranslatorInputModel, TranslatorOutputModel
from errors.api import incorrect_api_provider
from config import AIModels


class TranslatorProcessor(AbstractRemoteProcessor):
    def __init__(self):
        super().__init__()

        self.model_name = AIModels.translator_model

        self.system_prompt = """You are a translator. Your task - translate text to target language."""

    def __make_request_body(self, text: str, target_language: str):
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Translate this text to {target_language}: {text}"
                    }
                ]
            }
        ]
        match config.Modes.api_provider:
            case "openrouter":
                request_body = {
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": config.Constants.translator_max_output_tokens,
                }
                url = config.Links.openrouter_handler
            case "yandex":
                request_body = {
                    "modelUri": f"gpt://{config.Secrets.yandex_folder_id}/yandexgpt/latest",
                    "completionOptions": {
                        "stream": False,
                        "maxTokens": config.Constants.translator_max_output_tokens,
                    },
                    "messages": messages,
                }
                url = config.Links.yandex_ai_handler
            case _:
                raise incorrect_api_provider

        return {
            "url": url,
            "headers": self.headers,
            "json": request_body,
        }

    async def __call__(self, body: TranslatorInputModel) -> TranslatorOutputModel:
        request_body = self.__make_request_body(
            text=body.text,
            target_language=body.target_language,
        )

        async with ClientSession() as session:
            async with session.post(**request_body) as response:
                response.raise_for_status()
                data = await response.json()
                message = data["choices"][0]["message"]["content"]

        return TranslatorOutputModel(text=message)
