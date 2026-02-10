import base64
import os


def image_bytes_to_openrouter_string(image_bytes: bytes) -> str:
    b64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def find_nearest_icon(start_dir: str, filename: str = "derivative-zero-icon.ico", max_levels: int = 5):
    cur = os.path.abspath(start_dir)
    checked = set()
    for _ in range(max_levels):
        if not cur or cur in checked:
            break
        checked.add(cur)
        candidates = [
            os.path.join(cur, filename),
            os.path.join(cur, "docs", "images", filename),
            os.path.join(cur, "docs", filename),
            os.path.join(cur, "images", filename),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.normpath(c)
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    walk_limit = 200
    count = 0
    for root, dirs, files in os.walk(start_dir):
        if filename in files:
            return os.path.normpath(os.path.join(root, filename))
        count += 1
        if count > walk_limit:
            break

    return None


ai_consulter_prompt = """You are a science consulter.
    Your task - answer student's question about some studying text.
    You will be provided some piece of text that student is reading right now in the context.
    You need to make 100% correct answer on his question. 
    You can use text from context or your own knowledge.
    Use markdown formatting + LaTex for formulas.
"""
