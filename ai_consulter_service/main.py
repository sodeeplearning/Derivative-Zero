from fastapi import FastAPI, Response

from schemas.processors import AIConsulterInputModel, AIConsulterOutputModel
from processors.ai_consulter import AIConsulterProcessor


app = FastAPI(root_path="/ai-consulter")

processor = AIConsulterProcessor()


@app.post("/sync")
def process_ai_consulter_request(body: AIConsulterInputModel) -> AIConsulterOutputModel:
    result = processor(body=body)
    return result


@app.delete("/clear_chat_history")
async def clear_ai_assistant_chat_history():
    processor.clear_chat_history()
    return Response(status_code=200)


@app.post("/set_chat_history")
async def set_ai_assistant_chat_history(new_chat_history):
    processor.set_chat_history(new_chat_history)
    return Response(status_code=200)
