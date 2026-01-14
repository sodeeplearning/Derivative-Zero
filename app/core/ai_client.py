import requests
import base64
from typing import Literal


class AIClientError(Exception):
    ...


class AIClient:
    def __init__(self, url):
        self.url = url

    def ask(self, page_text, images, question) -> str:
        payload = {
            "context": page_text,
            "question": question,
            "images": [
                base64.b64encode(img).decode()
                for img in images
            ]
        }

        try:
            response = requests.post(
                self.url + "/ai-consulter/sync",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data["text"]

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

    def set_url(self, url):
        self.url = url

    def clear_chat_history(self):
        try:
            response = requests.delete(
                self.url + "/ai-consulter/clear_chat_history",
                timeout=40,
            )
            response.raise_for_status()

        except requests.exceptions.Timeout:
            raise AIClientError("⏱ Сервер не отвечает (timeout)")

        except requests.exceptions.ConnectionError:
            raise AIClientError("🔌 Не удалось подключиться к серверу")

        except Exception as e:
            raise AIClientError(f"💥 Неизвестная ошибка: {e}")

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
        try:
            response = requests.post(
                self.url + "/tts/async",
                json=payload,
                timeout=600,
            )
            response.raise_for_status()
            data = response.json()
            return data["audio_base64"]

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
