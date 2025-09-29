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

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {config.Secrets.openrouter_api_key}",
            "Content-Type": "application/json"
        }

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...

    @abstractmethod
    def __make_request_body(self, *args, **kwargs):
        ...
