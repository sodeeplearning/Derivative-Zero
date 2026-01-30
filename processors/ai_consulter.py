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

        self.base_system_prompt = """You are a science consulter.
        Your task - answer student's question about some studying text.
        You will be provided some piece of text that student is reading right now in the context.
        You need to make 100% correct answer on his question. 
        You can use text from context or your own knowledge.
        Use markdown formatting + LaTex for formulas.
        """

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
