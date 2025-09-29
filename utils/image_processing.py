import base64


def image_bytes_to_openrouter_string(image_bytes: bytes) -> str:
    b64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"
