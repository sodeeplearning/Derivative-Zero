from fastapi import FastAPI

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
from processors.ai_consulter import AIConsulterProcessor
from backend_logger import Logger


app = FastAPI(root_path="/ai-consulter")

processor = AIConsulterProcessor()


@app.post("/async", response_model=AIConsulterOutputModel)
@Logger.async_handler_logger("AI Consulter")
async def process_ai_consulter_request(body: AIConsulterInputModel) -> AIConsulterOutputModel:
    result = await processor(body=body)
    return result
