from fastapi import FastAPI, Response

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
from processors.ai_consulter import AIConsulterProcessor
from utils.text_processing import ai_answer_to_qt_html


app = FastAPI(root_path="/ai-consulter")

processor = AIConsulterProcessor()


@app.post("/sync")
def process_ai_consulter_request(body: AIConsulterInputModel) -> AIConsulterOutputModel:
    result = processor(body=body)

    if body.convert_to_html:
        result.text = ai_answer_to_qt_html(result.text)

    return result


@app.delete("/clear_chat_history")
async def clear_ai_assistant_chat_history():
    processor.clear_chat_history()
    return Response(status_code=200)


@app.post("/set_chat_history")
async def set_ai_assistant_chat_history(new_chat_history):
    processor.set_chat_history(new_chat_history)
    return Response(status_code=200)
