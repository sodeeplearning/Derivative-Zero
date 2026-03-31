import base64


def encode_audio_to_b64_string(content: bytes):
    return base64.b64encode(content).decode("utf-8")
