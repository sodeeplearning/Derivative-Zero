from fastapi import FastAPI

from schemas.processors import TranslatorInputModel, TranslatorOutputModel
from processors.translator import TranslatorProcessor
from backend_logger import Logger


app = FastAPI(root_path="/translator")

processor = TranslatorProcessor()


@app.post("/async")
@Logger.handler_logger("Translator")
async def process_translator_request(body: TranslatorInputModel) -> TranslatorOutputModel:
    result = await processor(body=body)
    return result
