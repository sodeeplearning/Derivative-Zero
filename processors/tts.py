from aiohttp import ClientSession

from .base import AbstractRemoteProcessor

from schemas.processors import TTSInputModel, TTSOutputModel
from utils.audio_processing import encode_audio_to_b64_string
import config


class AsyncTextToSpeechModel(AbstractRemoteProcessor):
    def __init__(self):
        super().__init__()

    def __make_request_body(self, body: TTSInputModel) -> dict:
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
            "headers": self.headers_mapping["yandex"],
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
