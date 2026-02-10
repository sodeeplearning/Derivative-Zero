import json
import os
from pathlib import Path


if os.name == "nt":
    base_data_dir = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "DerivativeZero"
else:
    base_data_dir = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "derivative_zero"

FILE = base_data_dir / "recent_books.json"
FILE.parent.mkdir(parents=True, exist_ok=True)


def load_books():
    if FILE.exists():
        return json.loads(FILE.read_text()).get("books", [])
    return []


def save_books(books):
    FILE.write_text(json.dumps({"books": books}, indent=2))
