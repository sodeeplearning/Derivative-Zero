import json
from pathlib import Path


FILE = Path("data/recent_books.json")
FILE.parent.mkdir(exist_ok=True)


def load_books():
    if FILE.exists():
        return json.loads(FILE.read_text()).get("books", [])
    return []


def save_books(books):
    FILE.write_text(json.dumps({"books": books}, indent=2))
