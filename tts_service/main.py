from fastapi import FastAPI

from processors.tts import AsyncTextToSpeechMMLM
from schemas.processors import TTSInputModel, TTSOutputModel
from backend_logger import Logger


app = FastAPI(root_path="/tts")

processor = AsyncTextToSpeechMMLM()


@app.post("/async")
@Logger.handler_logger("TTS")
async def process_tts_request(body: TTSInputModel) -> TTSOutputModel:
    result = await processor(body=body)
    return result
