from aiohttp import ClientSession

from .base import AbstractRemoteProcessor

from schemas.processors import TranslatorInputModel, TextModel
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
        return {
            "model": self.model_name,
            "messages": messages,
        }

    async def __call__(self, body: TranslatorInputModel) -> TextModel:
        json_body = self.__make_request_body(
            text=body.text,
            target_language=body.target_language,
        )

        async with ClientSession() as session:
            async with session.post(self.base_url, headers=self.headers, json=json_body) as response:
                response.raise_for_status()
                data = await response.json()
                message = data["choices"][0]["message"]["content"]

        return TextModel(text=message)
