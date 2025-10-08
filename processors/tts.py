from aiohttp import ClientSession
import base64

from .base import AbstractRemoteProcessor

from schemas.processors import TTSInputModel, TTSOutputModel
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

    @staticmethod
    def postprocess_content(content: bytes):
        return base64.b64encode(content).decode("utf-8")

    async def __call__(self, body: TTSInputModel) -> TTSOutputModel:
        request_data = self.__make_request_body(body=body)

        async with ClientSession() as session:
            async with session.post(**request_data) as response:
                response.raise_for_status()

        response_content = await response.read()
        audio_base64 = self.postprocess_content(response_content)

        return TTSOutputModel(
            audio_base64=audio_base64,
        )
