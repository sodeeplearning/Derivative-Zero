from openai import OpenAI
import config
from .base import BaseAbstractProcessor

from schemas.processors import TranslatorInputModel, TranslatorOutputModel



class TranslatorProcessor(BaseAbstractProcessor):
    def __init__(self):
        self.model_name = config.AIModels.translator_model

        self.client = OpenAI(
            api_key=config.Secrets.openrouter_api_key,
            base_url=config.Links.openrouter_handler,
        )

        self.system_prompt = """You are a translator. Your task - translate text to target language."""

    def __call__(self, body: TranslatorInputModel) -> TranslatorOutputModel:
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

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )
        output = chat_completion.choices[0].message.content

        return TranslatorOutputModel(
            text=output,
        )
