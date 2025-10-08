from fastapi import FastAPI

from processors.tts import AsyncTextToSpeechModel
from schemas.processors import TTSInputModel, TTSOutputModel


app = FastAPI()

processor = AsyncTextToSpeechModel()


@app.post("/tts")
async def process_tts_request(body: TTSInputModel) -> TTSOutputModel:
    result = await processor(body=body)
    return result
