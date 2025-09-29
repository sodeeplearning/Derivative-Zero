from dataclasses import dataclass

from os import environ
from dotenv import load_dotenv

load_dotenv()


class Secrets(dataclass):
    openrouter_api_key = environ["OPENROUTER_API_KEY"]


class DefaultAIModels(dataclass):
    ai_consult_model = "openai/gpt-4o-mini"
    translator_model = "openai/gpt-4o-mini"


class AIModels(dataclass):
    ai_consult_model = environ.get("AI_CONSULT_MODEL", DefaultAIModels.ai_consult_model)
    translator_model = environ.get("TRANSLATOR_MODEL", DefaultAIModels.translator_model)
