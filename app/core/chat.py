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
        self._media_content = dict()

    def clear_chat(self):
        self._chat = self._base_chat.copy()
        self._viewed_pages.clear()

    def get_chat(self):
        chat = self._chat.copy()
        for page_id in sorted(self._viewed_pages):
            chat[0]["content"].append({
                "type": "text",
                "text": f"Page {page_id} content: {self._media_content[page_id]["text"]}",
            })
            for image in self._media_content[page_id]["images"]:
                chat[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image_bytes_to_openrouter_string(image)},
                })
        return chat

    def update_content(self, window_content):
        self._media_content |= window_content["contents"]
        self._viewed_pages |= window_content["indexes"]

    def append_user_message(
            self,
            user_prompt: str,
            window_context: dict,
    ):
        self.update_content(window_context)
        page_info = f"\nPage user reading at the moment: {window_context["current_page_index"]}"

        new_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt + page_info,
                }
            ]
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
