from fastapi import FastAPI

from processors.tts import TTSPipelineProcessor
from schemas.processors import TTSInputModel, TTSOutputModel


app = FastAPI(root_path="/tts")

processor = TTSPipelineProcessor()


@app.post("/async")
async def process_tts_request(body: TTSInputModel) -> TTSOutputModel:
    result = await processor(body=body)
    return result
