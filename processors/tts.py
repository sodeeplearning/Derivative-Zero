from aiohttp import ClientSession
import base64
from io import BytesIO

from openai import OpenAI

from .base import BaseAbstractProcessor

from schemas.processors import TTSInputModel, TTSOutputModel
from utils.audio_processing import encode_audio_to_b64_string
import config


class AsyncTextToSpeechModel(BaseAbstractProcessor):
    def __init__(self):
        super().__init__()

    @staticmethod
    def __make_request_body(body: TTSInputModel) -> dict:
        data = {
            "text": body.text,
            "lang": "ru-RU",
            "voice": "filipp" if body.voice == "male" else "masha",
            "folderId": config.Secrets.yandex_folder_id,
            "format": "lpcm",
            "sampleRateHertz": 48_000,
        }
        return {
            "url": config.Links.tts_yandex,
            "headers": {
                "Authorization": f"Bearer {config.Secrets.yandex_api_key}",
                "Content-Type": "application/json"
            },
            "data": data,
            "stream": True,
        }

    async def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        request_data = self.__make_request_body(body=body)

        async with ClientSession() as session:
            async with session.post(**request_data) as response:
                response.raise_for_status()

        response_content = await response.read()
        audio_base64 = encode_audio_to_b64_string(response_content)

        return TTSOutputModel(
            audio_base64=audio_base64,
        )


class TextToSpeechMMLM(BaseAbstractProcessor):
    def __init__(self):
        self.client = OpenAI(
            base_url=config.Links.openrouter_handler,
            api_key=config.Secrets.openrouter_api_key,
        )
        self.model_name = config.AIModels.tts_mllm

        self.system_prompt = """You are a teacher that tries to explain some
        text (e.g. study book) to your students. Student gives you text of this book.
        Your task - make a speech version of the text."""

    def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        with self.client.audio.speech.with_streaming_response.create(
            input=body.text,
            voice="coral",
            instructions=self.system_prompt,
            model=self.model_name,
        ) as response:

            buffer = BytesIO()
            response.stream_to_file(buffer)
            audio_bytes = buffer.getvalue()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return TTSOutputModel(
            audio_base64=audio_base64,
        )
