import asyncio

from openai import AsyncClient

from .base import BaseAbstractProcessor

from schemas.processors import TTSInputModel, TTSOutputModel
from utils.audio_processing import encode_audio_to_b64_string


class AsyncTextToSpeechMMLM(BaseAbstractProcessor):
    def __init__(self, api_key: str, handler_link: str):
        self.client = AsyncClient(
            base_url=handler_link,
            api_key=api_key,
            timeout=600,
        )

        self.system_prompt = """You are a teacher that tries to explain some
        text (e.g. study book) to your students. Student gives you text of this book.
        Your task - make a speech version of the text."""

    async def __single_request(self, text: str, voice: str, model_name: str) -> str:
        response = await self.client.audio.speech.with_raw_response.create(
            input=text,
            voice=voice,
            instructions=self.system_prompt,
            model=model_name,
            response_format="mp3",
        )
        audio_base64 = encode_audio_to_b64_string(response.content)
        return audio_base64

    async def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(self.__single_request(text, body.voice, body.model_name))
                for text in body.texts
            ]
        text_results = [task.result() for task in tasks]

        return TTSOutputModel(
            audio_base64=text_results,
        )
