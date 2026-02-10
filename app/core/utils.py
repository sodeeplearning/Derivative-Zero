import base64


def image_bytes_to_openrouter_string(image_bytes: bytes) -> str:
    b64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


ai_consulter_prompt = """You are a science consulter.
    Your task - answer student's question about some studying text.
    You will be provided some piece of text that student is reading right now in the context.
    You need to make 100% correct answer on his question. 
    You can use text from context or your own knowledge.
    Use markdown formatting + LaTex for formulas.
"""
