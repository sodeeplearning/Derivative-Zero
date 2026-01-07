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

        self.chat_history = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                    }
                ]
            },
        ]

    def clear_chat_history(self):
        self.chat_history.clear()

    def set_chat_history(self, new_chat_history):
        self.chat_history = new_chat_history

    def __call__(self, body: AIConsulterInputModel) -> AIConsulterOutputModel:
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Context: {body.context}. Student's question: {body.question}"
                }
            ]
        }
        for image in body.images:
            user_message["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",
                    }
                }
            )

        self.chat_history.append(user_message)

        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.chat_history,
        )
        output = chat_completion.choices[0].message.content

        ai_message = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": output,
                }
            ]
        }
        self.chat_history.append(ai_message)

        return AIConsulterOutputModel(
            text=output,
        )
