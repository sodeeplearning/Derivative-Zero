import asyncio
from aiohttp import ClientSession

from openai import AsyncClient

from .base import BaseAbstractProcessor

from schemas.processors import TTSInputModel, TTSOutputModel
from utils.audio_processing import encode_audio_to_b64_string
import config


class AsyncTextToSpeechModel(BaseAbstractProcessor):
    def __init__(self):
        super().__init__()

    @staticmethod
    def __make_request_body(text: str, voice: str) -> dict:
        data = {
            "text": text,
            "lang": "ru-RU",
            "voice": "filipp" if voice == "male" else "masha",
            "folderId": config.Secrets.yandex_folder_id,
            "format": "lpcm",
            "sampleRateHertz": 48_000,
            "stream": True
        }
        return {
            "url": config.Links.tts_yandex,
            "headers": {
                "Authorization": f"Bearer {config.Secrets.yandex_api_key}",
                "Content-Type": "application/json"
            },
            "data": data,
        }

    async def __single_request(self, text: str, voice: str = "coral"):
        request_data = self.__make_request_body(text=text, voice=voice)

        async with ClientSession() as session:
            async with session.post(**request_data) as response:
                response.raise_for_status()
        response_content = await response.read()
        audio_base64 = encode_audio_to_b64_string(response_content)

        return audio_base64

    async def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(self.__single_request(text=text, voice=body.voice))
                for text in body.texts
            ]
        text_results = [task.result() for task in tasks]

        return TTSOutputModel(
            audio_base64=text_results,
        )


class AsyncTextToSpeechMMLM(BaseAbstractProcessor):
    def __init__(self):
        self.client = AsyncClient(
            base_url=config.Links.openrouter_handler,
            api_key=config.Secrets.openrouter_api_key,
        )
        self.model_name = config.AIModels.tts_mllm

        self.system_prompt = """You are a teacher that tries to explain some
        text (e.g. study book) to your students. Student gives you text of this book.
        Your task - make a speech version of the text."""

    async def __single_request(self, text: str, voice: str = "coral") -> str:
        response = await self.client.audio.speech.with_raw_response.create(
            input=text,
            voice=voice,
            instructions=self.system_prompt,
            model=self.model_name,
        )
        audio_base64 = encode_audio_to_b64_string(response.content)
        return audio_base64

    async def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        async with asyncio.TaskGroup() as task_group:
            tasks = [
                task_group.create_task(self.__single_request(text=text, voice=body.voice))
                for text in body.texts
            ]
        text_results = [task.result() for task in tasks]

        return TTSOutputModel(
            audio_base64=text_results,
        )


class TTSPipelineProcessor:
    def __init__(self):
        self.openai_tts = AsyncTextToSpeechMMLM()
        self.yandex_tts = AsyncTextToSpeechModel()

    async def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        match body.tts_provider:
            case "yandex":
                return await self.yandex_tts(body=body)
            case "openai":
                return await self.openai_tts(body=body)
            case _:
                raise ValueError(f"Incorrect TTS provider: {body.tts_provider}")
