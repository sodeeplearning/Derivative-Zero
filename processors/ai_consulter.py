from aiohttp import ClientSession

from .base import AbstractRemoteProcessor

from schemas.processors import AIConsulterInputModel, TextModel
from config import AIModels


class AsyncAIConsulterProcessor(AbstractRemoteProcessor):
    def __init__(self, max_output_tokens: int = 4096):
        super().__init__()

        self.max_output_tokens = max_output_tokens

        self.model_name = AIModels.ai_consult_model

        self.system_prompt = """You are a science consulter.
        Your task - answer student's question about some studying text.
        You will be provided some piece of text that student is reading right now in the context.
        You need to make 100% correct answer on his question. 
        You can use text from context or your own knowledge.
        """

    def __make_request_body(self, body: AIConsulterInputModel):
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

        return {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_output_tokens,
        }

    async def __call__(self, body: AIConsulterInputModel) -> TextModel:
        json_body = self.__make_request_body(body=body)

        async with ClientSession() as session:
            async with session.post(self.base_url, headers=self.headers, json=json_body) as response:
                response.raise_for_status()
                data = await response.json()
                message = data["choices"][0]["message"]["content"]

        return TextModel(text=message)
