from fastapi import FastAPI

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
from processors.ai_consulter import AsyncAIConsulterProcessor


app = FastAPI()

processor = AsyncAIConsulterProcessor()


@app.post("/ai_consulter")
async def process_ai_consulter_request(body: AIConsulterInputModel) -> AIConsulterOutputModel:
    result = await processor(body=body)
    return result
