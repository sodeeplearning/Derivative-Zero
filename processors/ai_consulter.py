import json
from openai import AsyncOpenAI

from .base import BaseAbstractProcessor

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
import config


class AIConsulterProcessor(BaseAbstractProcessor):
    def __init__(self):
        super().__init__()

        self.client = AsyncOpenAI(
            api_key=config.Secrets.openrouter_api_key,
            base_url=config.Links.openrouter_handler,
        )

    async def __call__(self, body: AIConsulterInputModel) -> AIConsulterOutputModel:
        chat = json.loads(body.chat)

        chat_completion = await self.client.chat.completions.create(
            model=body.model_name,
            messages=chat,
        )
        output = chat_completion.choices[0].message.content

        return AIConsulterOutputModel(
            text=output,
        )
