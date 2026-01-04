from dataclasses import dataclass
from os import environ
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Links:
    openrouter_handler = environ.get("OPENROUTER_HANDLER", "https://api.proxyapi.ru/openrouter/v1/chat/completions")
    yandex_ai_handler = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    tts_yandex = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


@dataclass
class Secrets:
    openrouter_api_key = environ["OPENROUTER_API_KEY"]
    yandex_api_key = environ["YANDEX_API_KEY"]
    yandex_folder_id = environ["YANDEX_FOLDER_ID"]


@dataclass
class DefaultAIModels:
    ai_consult_model = "openai/gpt-4o-mini"
    translator_model = "openai/gpt-4o-mini"


@dataclass
class AIModels:
    ai_consult_model = environ.get("AI_CONSULT_MODEL", DefaultAIModels.ai_consult_model)
    translator_model = environ.get("TRANSLATOR_MODEL", DefaultAIModels.translator_model)


@dataclass
class Constants:
    ai_consulter_max_output_tokens = 8192
    translator_max_output_tokens = 10_000
