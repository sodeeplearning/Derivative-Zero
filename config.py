from dataclasses import dataclass
from os import environ
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


@dataclass
class Modes:
    api_provider: Literal["yandex", "openrouter"] = environ.get("API_PROVIDER", "yandex")


@dataclass
class Links:
    yandex_ai_handler = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    openrouter_handler = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


@dataclass
class Secrets:
    openrouter_api_key = environ.get("OPENROUTER_API_KEY")
    yandex_api_key = environ.get("YANDEX_API_KEY")
    yandex_folder_id = environ.get("YANDEX_FOLDER_ID")

    def __post_init__(self):
        missing_field = None

        match Modes.api_provider:
            case "yandex":
                if not self.yandex_api_key:
                    missing_field = "YANDEX_API_KEY"
                if not self.yandex_folder_id:
                    missing_field = "YANDEX_FOLDER_ID"

            case "openrouter":
                if not self.openrouter_api_key:
                    missing_field = "OPENROUTER_API_KEY"

        if missing_field:
            raise ValueError(f"""You've chosen provider '{Modes.api_provider}'
             but didn't provide '{missing_field}' in .env file""")


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
