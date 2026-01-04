from fastapi import FastAPI

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
from processors.ai_consulter import AIConsulterProcessor


app = FastAPI(root_path="/ai-consulter")

processor = AIConsulterProcessor()


@app.post("/sync")
def process_ai_consulter_request(body: AIConsulterInputModel) -> AIConsulterOutputModel:
    result = processor(body=body)
    return result
