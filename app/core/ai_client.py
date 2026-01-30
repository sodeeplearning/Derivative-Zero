import requests
import base64
import warnings

from typing import Callable


class AIClientError(Exception):
    ...


def safe_request(func: Callable):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except requests.exceptions.Timeout:
            raise AIClientError("⏱ Сервер не отвечает (timeout)")
        except requests.exceptions.ConnectionError:
            raise AIClientError("🔌 Не удалось подключиться к серверу")
        except requests.exceptions.HTTPError as e:
            raise AIClientError(
                f"❌ Ошибка сервера: {e.response.status_code}"
            )
        except ValueError:
            raise AIClientError("📄 Сервер вернул не JSON")
        except Exception as e:
            raise AIClientError(f"💥 Неизвестная ошибка: {e}")

    return wrapper


class AIClient:
    def __init__(self, url):
        self.url = url

    def set_url(self, url):
        self.url = url

    @safe_request
    def ask(self, page_text, images, question) -> str:
        payload = {
            "context": page_text,
            "question": question,
            "images": [
                base64.b64encode(img).decode()
                for img in images
            ]
        }

        response = requests.post(
            self.url + "/ai-consulter/sync",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["text"]

    def clear_chat_history_no_exceptions(self):
        try:
            requests.delete(
                self.url + "/ai-consulter/clear_chat_history",
                timeout=40,
            )
        except Exception as e:
            warnings.warn(f"Trying to update chat history caused error: {e}")

    @safe_request
    def clear_chat_history(self):
        response = requests.delete(
            self.url + "/ai-consulter/clear_chat_history",
            timeout=40,
        )
        response.raise_for_status()

    @safe_request
    def get_speech(
            self,
            texts: str | list[str],
            voice: str = "coral",
    ) -> str:
        if isinstance(texts, str):
            texts = [texts]

        payload = {
            "texts": texts,
            "voice": voice,
        }

        response = requests.post(
            self.url + "/tts/async",
            json=payload,
            timeout=600,
        )
        response.raise_for_status()
        data = response.json()

        return data["audio_base64"]

    @safe_request
    def translate_text(self, text: str, target_language: str = "ru") -> str:
        payload = {
            "text": text,
            "target_language": target_language,
        }

        response = requests.post(
            self.url + "/translator/async",
            json=payload,
            timeout=200,
        )
        response.raise_for_status()
        data = response.json()

        return data["text"]
