from fastapi import FastAPI

from processors.tts import AsyncTextToSpeechModel
from schemas.processors import TTSInputModel, TTSOutputModel


app = FastAPI(root_path="/tts")

processor = AsyncTextToSpeechModel()


@app.post("/async")
async def process_tts_request(body: TTSInputModel) -> TTSOutputModel:
    result = await processor(body=body)
    return result
