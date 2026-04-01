from openai import AsyncOpenAI
from .base import BaseAbstractProcessor

from schemas.processors import TranslatorInputModel, TranslatorOutputModel



class TranslatorProcessor(BaseAbstractProcessor):
    def __init__(self, api_key: str, handler_link: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=handler_link,
            timeout=600,
        )

        self.system_prompt = """You are a translator. Your task - translate text to target language."""

    async def __call__(self, body: TranslatorInputModel) -> TranslatorOutputModel:
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
                        "text": f"Translate this text to {body.target_language}: {body.text}"
                    }
                ]
            }
        ]

        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model=body.model_name,
        )
        output = chat_completion.choices[0].message.content

        return TranslatorOutputModel(
            text=output,
        )
