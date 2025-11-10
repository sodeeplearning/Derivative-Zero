from abc import ABC, abstractmethod

import config


class BaseAbstractProcessor(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class AbstractRemoteProcessor(BaseAbstractProcessor):
    def __init__(self):
        self.model_name: str = "Abstract model name"
        self.system_prompt: str = "Abstract system prompt"

        self.headers_mapping = {
            "openrouter": {
                "Authorization": f"Bearer {config.Secrets.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            "yandex": {
                "Authorization": f"Bearer {config.Secrets.yandex_api_key}",
                "Content-Type": "application/json"
            },
        }

    @property
    def headers(self):
        return self.headers_mapping[config.Modes.api_provider]


    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
