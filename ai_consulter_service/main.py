from fastapi import FastAPI

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
from processors.ai_consulter import AIConsulterProcessor
from utils.text_processing import ai_answer_to_qt_html


app = FastAPI(root_path="/ai-consulter")

processor = AIConsulterProcessor()


@app.post("/async", response_model=AIConsulterOutputModel)
async def process_ai_consulter_request(body: AIConsulterInputModel) -> AIConsulterOutputModel:
    result = await processor(body=body)

    if body.convert_to_html:
        result.text = ai_answer_to_qt_html(result.text)

    return result
