from utils.image_processing import image_bytes_to_openrouter_string
import config


class UserChat:
    def __init__(
            self,
            system_prompt: str = config.Prompts.ai_consulter
    ):
        self._base_chat = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt,
                    }
                ]
            },
        ]
        self._chat = self._base_chat.copy()
        self._viewed_pages = set()

    def clear_chat(self):
        self._chat = self._base_chat.copy()
        self._viewed_pages.clear()

    def get_chat(self):
        return self._chat

    def append_user_message(
            self,
            page_number: int,
            page_content: str,
            page_images: list[bytes],
            user_prompt: str,
    ):
        text_message = f"Student's question: {user_prompt}"
        media_content = []

        if page_number not in self._viewed_pages:
            self._viewed_pages.add(page_number)
            text_message += f"\nContext: {page_content}"

            for image in page_images:
                media_content.append({
                    "type": "image_url",
                    "image_url": {"url": image_bytes_to_openrouter_string(image)}
                })

        new_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text_message,
                }
            ] + media_content
        }
        self._chat.append(new_message)

    def append_assistant_message(self, message: str):
        new_message = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": message,
                }
            ]
        }
        self._chat.append(new_message)
