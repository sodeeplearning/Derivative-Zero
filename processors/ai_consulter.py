from aiohttp import ClientSession

from .base import AbstractRemoteProcessor

from schemas.processors import AIConsulterInputModel, TextModel
from errors.api import incorrect_api_provider
import config


class AsyncAIConsulterProcessor(AbstractRemoteProcessor):
    def __init__(self):
        super().__init__()
        self.model_name = config.AIModels.ai_consult_model

        self.system_prompt = """You are a science consulter.
        Your task - answer student's question about some studying text.
        You will be provided some piece of text that student is reading right now in the context.
        You need to make 100% correct answer on his question. 
        You can use text from context or your own knowledge.
        """

    def __make_request_body(self, body: AIConsulterInputModel) -> dict:
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
                        "text": f"Context: {body.context}. Student's question: {body.question}"
                    }
                ]
            }
        ]
        for image in body.images:
            messages[1]["content"].append(
                {
                    "type": "image_url",
                    "image_url": image,
                }
            )

        match config.Modes.api_provider:
            case "openrouter":
                request_body = {
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": config.Constants.ai_consulter_max_output_tokens,
                }
                url = config.Links.openrouter_handler

            case "yandex":
                request_body = {
                    "modelUri": f"gpt://{config.Secrets.yandex_folder_id}/yandexgpt/latest",
                    "completionOptions": {
                        "stream": False,
                        "maxTokens": config.Constants.ai_consulter_max_output_tokens,
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

    async def __call__(self, body: AIConsulterInputModel) -> TextModel:
        request_body = self.__make_request_body(body=body)

        async with ClientSession() as session:
            async with session.post(**request_body) as response:
                response.raise_for_status()
                data = await response.json()
                message = data["choices"][0]["message"]["content"]

        return TextModel(text=message)
