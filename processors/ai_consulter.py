from openai import OpenAI

from .base import BaseAbstractProcessor

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
import config


class AIConsulterProcessor(BaseAbstractProcessor):
    def __init__(self):
        super().__init__()
        self.model_name = config.AIModels.ai_consult_model

        self.client = OpenAI(
            api_key=config.Secrets.openrouter_api_key,
            base_url=config.Links.openrouter_handler,
        )

        self.system_prompt = """You are a science consulter.
        Your task - answer student's question about some studying text.
        You will be provided some piece of text that student is reading right now in the context.
        You need to make 100% correct answer on his question. 
        You can use text from context or your own knowledge.
        """

    def __call__(self, body: AIConsulterInputModel) -> AIConsulterOutputModel:
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
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",
                    }
                }
            )

        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        output = chat_completion.choices[0].message.content

        return AIConsulterOutputModel(
            text=output,
        )
